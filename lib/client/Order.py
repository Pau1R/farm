from datetime import date
from lib.Gui import Gui
import time
import math

class Order:
	app = None
	GUI = None
	spool_logic = None

	# order attributes:
	order_id = 1
	name = ''
	date = None
	user_id = 1
	status = 'creating' # client: creating, validate, validated, rejected, prepayed, printed, at_delivery, no_spools
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
	conditions = ''
	comment = ''
	color_id = 0
	support_remover = ''

	# files
	sketches = []
	model_file = ''

	# evaluation data
	plastic_type = ''
	printer_type = ''
	weight = 0
	time = 0.0
	support_time = 0
	layer_hight = 0.0

	# payment and booking info
	price = 0.0
	pay_code = 0
	prepayed = 0.0
	prepayment_percent = 0
	booked = []
	booked_time = 0
	
	def __init__(self, app, order_id):
		self.app = app
		self.order_id = order_id
		self.date = date.today()
		self.spools = self.app.equipment.spools
		self.spool_logic = self.app.equipment.spool_logic

	def reset(self):
		self.order_id = self.get_next_free_id(self.app.orders)
		self.status = 'creating'

	def get_next_free_id(self, orders):
		ids = []
		for order in orders:
			ids.append(int(order.order_id))
		ids.sort()
		ids = list(dict.fromkeys(ids))
		id = 1
		for elem in ids:
			if elem == id:
				id += 1
			else:
				break
		return id

	def set_price(self):
		gram_price = self.app.equipment.spool_logic.get_gram_price(self.color_id, self.plastic_type)	# cost of one gramm of plastic
		plastic_price = self.weight * self.quantity * gram_price  										# total plastic price for order
		print_cost = self.app.equipment.print_cost(self.printer_type)  									# cost of one hour for printer
		time_price = (self.time / 60) * print_cost														# cost of all printer working time
		supports_price = self.get_supports_price()
		rounded_price = math.ceil((plastic_price + time_price) / 10) * 10  # round to upper side
		self.price = int(rounded_price + supports_price)
		self.app.db.update_order(self)

	def get_prepayment_price(self):
		prepay_price = (self.prepayment_percent / 100) * self.price
		prepay_price = math.ceil(prepay_price / 10) * 10

	def is_prepayed(self):
		if self.is_free_start:
			return True
		prepay_price = (self.prepayment_percent / 100) * self.price
		prepay_price = math.ceil(prepay_price / 10) * 10
		if self.prepayed < prepay_price:
			return False
		return True

	def get_supports_price(self):
		price = 0
		if self.support_remover == 'Компания':
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
		return self.booked

	def remove_reserve(self):
		for book in self.booked:
			spool = self.spool_logic.get_spool(book[0])
			if spool.booked >= book[1]:
				spool.booked -= book[1]
		self.booked_time = 0
		self.color_id = 0
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
		if self.type == 'any':
			return self.app.settings.get('basic_plastic_types').split(',')
		return [self.type]

	def get_object_date(self, element):
		return element.date

	def completion_estimate_date(self):
		date_ = date.today()
		# TODO: write algorithm to calculate completion date
		return self.app.functions.russian_date(date_)