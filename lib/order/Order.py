from datetime import timedelta, datetime, date, time
from lib.Gui import Gui
import math
import random

class Order:
	app = None
	GUI = None
	spool_logic = None

	# order attributes:
	id = 1
	name = ''
	date = None
	user_id = 1
	type = ''
	physical_status = '' # preparing, in_line, printing, printed
	logical_status = 'creating' # client: creating, validate, validated, rejected, prepayed, printed, at_delivery, no_spools, in_pick-up, issued, client_refused
	# who can change order status to another:
	# - client:
	#   - creating: validate
	#   - validated
	# - designer:
	#   - validate
	# - bot:
	#   - validated: prepayed
	assinged_designer_id = 0 # not used yet
	priority = 0

	# user settings
	quantity = 1
	quality = ''
	comment = ''
	color_id = 0
	support_remover = ''

	# files
	sketches = []
	model_file = ''
	link = ''

	# evaluation data and process
	design_time = 0  # TODO:
	print_time = 0   #       add to db
	plastic_type = ''
	printer_type = ''
	weight = 0
	completion_date = None
	start_datetime = None # date and time when order started printing
	support_time = 0
	layer_hight = 0.0

	# payment, booking and delivery info
	price = 0.0
	pay_code = 0
	payed = 0.0
	prepayment_percent = 0
	booked = []
	booked_time = 0
	delivery_code = 0
	delivery_user_id = 0
	
	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.date = datetime.today()
		self.spools = self.app.equipment.spools
		self.spool_logic = self.app.equipment.spool_logic

	def set_price(self):
		gram_price = self.app.equipment.spool_logic.get_gram_price(self.color_id, self.plastic_type)	# cost of one gramm of plastic
		plastic_price = self.weight * self.quantity * gram_price  										# total plastic price for order
		design_price = self.design_time / 60 * 1000														# cost for 3d design, 1000 rub
		printer_cost = self.app.equipment.printer_cost(self.printer_type)  								# cost of one hour for printer
		time_price = (self.get_printing_time() / 60) * printer_cost										# cost of all printer working time
		supports_price = self.get_supports_price()
		if self.support_remover == 'Компания':
			supports_price = 0
		rounded_price = math.ceil((plastic_price + design_price + time_price) / 10) * 10  # round to upper side
		self.price = int(rounded_price + supports_price)
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
		setting = int(self.app.settings.get('support_remove_price'))
		price = int(self.support_time * self.quantity * setting)
		price = math.ceil(price / 10) * 10
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
		money_payed = 0
		for chat in self.app.chats:
			if chat.user_id == self.user_id:
				money_payed = chat.user.money_payed
		if self.price < int(self.app.settings.get('prepayment_free_max')) and self.price < (money_payed / 4):
			return True
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
		self.booked_time = 0
		self.color_id = 0
		self.completion_date = None
		self.app.db.update_order(self)

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
			return self.app.settings.get('basic_plastic_types').split(',')
		return [self.type]

	def get_object_date(self, element):
		return element.date

	def set_completion_date(self):
		self.completion_date = self.app.order_logic.get_completion_date(50, self.printer_type) # TODO
		# self.completion_date = self.app.order_logic.get_completion_date(self.time, self.printer_type)
		self.app.db.update_order(self)

	def order_payed(self, amount):
		self.payed += amount
		if self.is_prepayed():
			self.physical_status = 'in_line'
			chat = self.app.get_chat(self.user_id)
			chat.user.orders_canceled = 0
			if self.status == 'in_pick-up' and self.delivery_user_id != 0:
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
		return self.price - self.payed