from datetime import timedelta, datetime, date
from datetime import time as date_time
import time

class Order_logic:
	app = None

	def __init__(self, app):
		self.app = app
		self.orders = app.orders

	def remove_unpaid_reserves(self):
		now = int(time.time())
		for order in self.orders:
			if not order.is_prepayed() and order.booked:
				if now > order.booked_time + 1800: # 30 minutes to prepay
					order.remove_reserve()
					chat = self.app.get_chat(order.user_id)
					chat.user.order_GUI.show_booking_canceled(self)

	def get_order_by_id(self, order_id):
		for order in self.orders:
			if order.id == order_id:
				return order

	def get_client_orders(self, user_id):
		orders = []
		for order in self.orders:
			if order.user_id == user_id:
				orders.append(order)
		return orders

	def get_orders_by_type(self, orders, type_):
		if type(type_) == str:
			type_ = [type_]
		orders_ = []
		for order in orders:
			designer = order.assinged_designer_id
			if order.type in type_:
				orders_.append(order)
		return orders_

	def get_orders_by_status(self, orders, status):
		if type(status) == str:
			status = [status]
		orders_ = []
		for order in orders:
			designer = order.assinged_designer_id
			if order.logical_status in status:
				orders_.append(order)
		return orders_

	def get_orders_by_user_id(self, orders, user_id):
		orders_ = []
		for order in orders:
			designer = order.assinged_designer_id
			if not user_id or not designer or designer == user_id:
				orders_.append(order)
		return orders_

	def convert_orders_to_buttons(self, orders):
		orders.copy().sort(key=self.get_object_date)
		buttons = []
		for order in orders:
			buttons.append([str(order.id) + ': ' + order.name, order.id])
		return buttons

	def get_order_by_pay_code(self, pay_code):
		for order in self.orders:
			if order.pay_code == pay_code:
				return order

	def get_order_by_delivery_code(self, delivery_code):
		for order in self.orders:
			if order.delivery_code == delivery_code:
				return order

	def count_all_time(self, printer_type):
		scheduled_time = 0
		for order in self.orders:
			if order.physical_status in ['in_line', 'printing'] and (order.printer_type == printer_type or printer_type == '*'):
				then = order.start_datetime
				now = datetime.today()
				used_time = 0
				if now.day == then.day:
					used_time = (then.hour * 60) + then.minute - (then.hour * 60) + then.minute
				else:
					used_time = (9 + 10) * 60 - (then.hour * 60) + then.minute # Count first day.  starts at 9 am for a 10 hour shift
					used_time += ((now - then).days - 1) * 10 * 60 # count days in between
					used_time += (now.hour * 60 + now.minute) - 9 * 60 # Count last day.
				# scheduled_time += order.time - used_time
				scheduled_time += 50 - used_time # TODO: redo time calculation using gcode table
		return scheduled_time

	def get_completion_date(self, order_time, printer_type):
		average_load = self.app.printer_logic.get_average_load(printer_type)		# average time to begin this order
		end_time = average_load + order_time										# add order time
		add_days = 0
		difference = datetime.today() - datetime.combine(date.today(), date_time(9, 0))
		difference = difference.total_seconds()
		if difference > 60 * 10:													# take in account if current day working hours have ended
			difference = 0
			add_days = 1
		if difference < 0 :
			difference = 0
		end_time += difference														# take in account time of day, starting from 9 am
		end_time += 60 * 5															# add buffer time of 5 hours (near time)
		days = end_time / (60 * 10)													# get amount of days to finish this order. Daily work hours: 10
		days += add_days
		days = int(days * 1.2)														# add buffer to days (far time)
		return date.today() + timedelta(days=days)

	def get_object_date(self, object):
		return object.date