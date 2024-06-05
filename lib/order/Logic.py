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
					chat.user.client_order.show_booking_canceled(self)

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
			if order.print_status in ['in_line', 'printing'] and order.printer_type == printer_type:
				then = order.start_datetime
				now = datetime.today()
				used_time = 0
				if now.day == then.day:
					used_time = (then.hour * 60) + then.minute - (then.hour * 60) + then.minute
				else:
					used_time = (9 + 10) * 60 - (then.hour * 60) + then.minute # Count first day.  starts at 9 am for a 10 hour shift
					used_time += ((now - then).days - 1) * 10 * 60 # count days in between
					used_time += (now.hour * 60 + now.minute) - 9 * 60 # Count last day.
				scheduled_time += order.time - used_time
		return scheduled_time
