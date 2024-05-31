from datetime import date
from lib.Gui import Gui
import time

class Order:
	app = None
	GUI = None

	assinged_designer_id = ''

	user_id = ''
	order_id = 1

	status = 'creating' # client: creating, validate, validated, rejected, prepayed, printed, at_delivery, no_spools
	# who can change order status to another:
	# - client:
	#   - creating: validate
	#   - validated
	# - designer:
	#   - validate
	# - bot:
	#   - validated: prepayed

	name = ''
	date = None

	plastic_type = ''
	color_id = 0
	printer_type = ''
	layer_hight = 0.0
	priority = 0
	weight = 0
	time = 0.0
	quantity = 1
	support_time = 0
	support_remover = ''
	conditions = ''
	comment = ''
	spool_logic = None

	start_time_estimate = None
	end_time_estimate = None
	
	# price_estimate = 0.0
	price = 0.0
	prepayed = 0.0
	prepayment_percent = 0
	pay_code = ''

	booked = []
	booked_time = 0 # TODO: add field to db

	sketches = []
	model_file = ''

	messages = []

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
		self.price = int(plastic_price + time_price)

	def is_prepayed(self):
		prepay_price = (self.prepayment_percent / 100) * self.price + 5 # use a buffer of 5 rub for rounding errors
		if order.prepayed < prepay_price:
			return False
		return True

	def is_free_start(self):
		money_payed = 0
		for chat in self.app.chats:
			if chat.user_id == order.user_id:
				money_payed = chat.user.money_payed
		if self.price < int(self.app.settings.get('prepayment_free_max')) and self.price < (money_payed / 2):
			return True
		return False

	def reserve_plastic(self, statuses, color_id):
		self.booked = self.app.equipment.spool_logic.book(statuses, self.type, color_id, self.weight, self.quantity)
		self.booked_time = int(time.time())
		return self.booked

	def remove_reserve(self):
		for book in self.booked:
			spool = self.spool_logic.get_spool(book[0])
			if spool.booked >= book[1]:
				spool.booked -= book[1]
		self.booked_time = 0

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