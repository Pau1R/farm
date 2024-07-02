from datetime import timedelta, datetime, date
import time
import math
import random

class Order:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = datetime.today()
		self.spools = self.app.equipment.spools
		self.spool_logic = self.app.equipment.spool_logic
		self.name = ''
		self.user_id = 1
		self.type = ''
		self.physical_status = '' # preparing, in_line, printing, printed
		self.logical_status = 'creating' # client: creating, validate, validated, rejected, prepayed, printed, at_delivery, no_spools, in_pick-up, issued, client_refused
		# who can change order status to another:
		# - client:
		#   - creating: validate
		#   - validated
		# - designer:
		#   - validate
		# - bot:
		#   - validated: prepayed
		self.assigned_designer_id = 0 # not used yet
		self.priority = 0

		# user settings
		self.quantity = 1
		self.quality = ''
		self.comment = ''
		self.color_id = 0
		self.support_remover = ''

		# files
		self.sketches = []
		self.model_file = ''
		self.link = ''

		# evaluation data and process
		self.design_time = 0
		self.print_time = 0
		self.plastic_type = ''
		self.printer_type = ''
		self.weight = 0
		self.completion_date = None
		self.start_datetime = None # date and time when order started printing
		self.support_time = 0
		self.layer_height = 0.0

		# payment, booking and delivery info
		self.price = 0.0
		self.pay_code = 0
		self.payed = 0.0
		self.prepayment_percent = 0
		self.booked = []
		self.booked_time = 0
		self.delivery_code = 0
		self.delivery_user_id = 0

	def set_price(self):
		if not self.prepayment_percent:
			self.prepayment_percent = int(self.app.setting.get('prepayment_percent'))
		gram_price = self.app.equipment.spool_logic.get_gram_price(self.color_id, self.plastic_type)	# cost of one gramm of plastic
		plastic_price = self.weight * self.quantity * gram_price  										# total plastic price for order
		design_price = self.design_time / 60 * 1000														# cost for 3d design, 1000 rub
		printer_cost = self.app.equipment.printer_cost(self.printer_type)  								# cost of one hour for printer
		time_price = (self.get_printing_time() / 60) * printer_cost										# cost of all printer working time
		supports_price = self.get_supports_price()														# cost of removing supports
		bring_to_delivery_price = 50																	# cost of walking to delivery
		delivery_price = 50																				# cost of delivery worker time
		if self.support_remover == 'Клиент':
			supports_price = 0
		total_price = plastic_price + design_price + time_price + supports_price + bring_to_delivery_price + delivery_price
		self.price = int(math.ceil((total_price) / 10) * 10)  # round to upper side by tens
		self.app.db.update_order(self)

	def get_printing_time(self):
		gcode_time = self.app.gcode_logic.get_all_time(self)
		if gcode_time == 0:
			return self.print_time
		return gcode_time

	def get_prepayment_price(self):
		if self.price < 300:
			prepay_price = self.price
		else:
			prepay_price = (self.prepayment_percent / 100) * self.price
			prepay_price = math.ceil(prepay_price / 10) * 10
		return prepay_price

	def get_remaining_prepayment(self):
		return int(self.get_prepayment_price() - self.payed)

	def is_prepayed(self):
		if self.is_free_start():
			return True
		prepay_price = self.get_prepayment_price()
		if self.payed < prepay_price:
			return False
		return True

	def is_payed(self):
		if self.payed >= self.price:
			return True
		return False

	def get_supports_price(self):
		setting = int(self.app.setting.get('support_remove_price'))
		price = int(self.support_time * self.quantity * setting)
		price = int(math.ceil(price / 10) * 10)
		return price

	def set_pay_code(self):
		if self.pay_code == 0:
			used_codes = [0]
			code = 0
			code_upper = 99
			if len(self.app.orders) > 80:
				code_upper = 999
			for order_ in self.app.orders:
				used_codes.append(order_.pay_code)
			while code in used_codes:
				code = random.randint(10, code_upper)
			self.pay_code = code
			self.app.db.update_order(self)

	def is_free_start(self):
		# money_payed = 0
		# for chat in self.app.chats:
		# 	if chat.user_id == self.user_id:
		# 		money_payed = chat.user.money_payed
		# if self.price < int(self.app.setting.get('prepayment_free_max')) and self.price < (money_payed / 4):
		# 	return True
		return False

	def reserve_plastic(self, statuses, color_id):
		self.booked = self.app.equipment.spool_logic.book(statuses, self.plastic_type, color_id, self.weight, self.quantity)
		self.booked_time = int(time.time())
		self.app.db.update_order(self)
		self.set_completion_date()
		return self.booked

	def remove_reserve(self):
		for book in self.booked:
			spool = self.spool_logic.get_spool(book[0])
			if spool.booked >= book[1]:
				spool.booked -= book[1]
		self.booked = []
		self.booked_time = 0
		self.color_id = 0
		self.completion_date = None
		self.app.db.update_order(self)

	def booking_canceled(self):
		self.logical_status = 'validated'
		self.remove_reserve()
		chat = self.app.get_chat(self.user_id)
		chat.user.order_GUI.show_booking_canceled(self)

	def min_weight(self): # minimum weight of one spool
		if self.weight < 300:
			limit = self.weight
		else:
			limit = 300
		total_weight = self.weight * self.quantity
		if total_weight < 300:
			limit = total_weight
		return limit

	def plastic_types(self):
		if self.type == 'basic':
			return self.app.setting.get('basic_plastic_types').split(',')
		return [self.type]

	def get_object_date(self, element):
		return element.created

	def set_completion_date(self):
		print_time = self.get_gcodes_all_time()
		if not print_time:
			print_time = self.print_time
		self.completion_date = self.app.order_logic.get_completion_date(print_time, self.printer_type)
		self.app.db.update_order(self)

	def get_gcodes(self):
		gcodes = []
		for gcode in self.app.gcodes:
			if gcode.order_id == self.id:
				gcodes.append(gcode)
		return gcodes

	def get_gcodes_all_time(self):
	    return sum(gcode.duration for gcode in self.get_gcodes())

	def get_gcodes_future_time(self):
	    total_duration = 0
	    for gcode in self.get_gcodes():
	        if gcode.start_datetime:
	            time_passed = (datetime.today() - gcode.start_datetime).total_seconds() / 60  # Convert to minutes
	            if time_passed < gcode.duration:  # Only consider remaining time
	                remaining_duration = gcode.duration - time_passed
	                total_duration += max(0, remaining_duration)  # Ensure no negative duration
	    return total_duration

	def get_gcodes_past_time(self):
	    return self.get_gcodes_all_time() - self.get_gcodes_future_time()

	def order_payed(self, amount):
		self.payed += amount
		text = f'К заказу {self.name} поступил платеж в размере {amount} рублей'
		chat = self.app.get_chat(self.user_id)
		chat.user.GUI.tell(text)

		if self.is_prepayed():
			if self.type == 'sketch':
				self.logical_status = 'waiting_for_design'
			elif self.type == 'item':
				self.logical_status = 'waiting_for_item'
			else:
				self.logical_status = ''
				self.physical_status = 'in_line'
			chat = self.app.get_chat(self.user_id)
			chat.user.orders_canceled = 0
			if self.physical_status == 'in_pick-up' and self.delivery_user_id != 0:
				chat = self.app.get_chat(self.delivery_user_id)
				chat.user.delivery.show_order_payed(self)

	def set_delivery_code(self):
		used_codes = [0]
		code = 0
		code_upper = 99
		if len(self.app.orders) > 80:
			code_upper = 999
		for order_ in self.app.orders:
			used_codes.append(order_.delivery_code)
		while code in used_codes:
			code = random.randint(10, code_upper)
		self.delivery_code = code
		self.app.db.update_order(self)

	def remaining_payment(self):
		return int(self.price - self.payed)

	def remove(self):
		self.remove_reserve()
		self.app.orders.remove(self)
		self.app.db.remove_order(self)