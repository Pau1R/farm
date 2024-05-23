from datetime import date
from lib.Gui import Gui

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

	start_time_estimate = None
	end_time_estimate = None
	
	# price_estimate = 0.0
	price = 0.0
	prepayed = 0.0
	prepayment_percent = 0
	pay_code = '' # TODO: add field to database table

	sketches = []
	model_file = ''

	messages = []

	def __init__(self, app, order_id):
		self.app = app
		self.order_id = order_id
		self.date = date.today()
		# self.GUI = Gui(app, app.chat)

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
		if self.color_id != 0:
			for spool in self.app.equipment.spools:
				if spool.color_id == self.color_id and spool.type == self.plastic_type:
					gram_price = spool.price/spool.weight
					break
		else:
			gram_price = self.app.equipment.spools_average_price(self.plastic_type)

		plastic_price = self.weight * self.quantity * gram_price
		for type_ in self.app.equipment.printer_types:
			if type_.name == self.printer_type:
				printer_hour_cost = type_.hour_cost
		time_price = (self.time / 60) * printer_hour_cost
		self.price = int(plastic_price + time_price)