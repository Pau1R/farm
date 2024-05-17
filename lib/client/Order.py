from datetime import date
from lib.Gui import Gui

class Order:
	app = None
	GUI = None

	assinged_designer_id = ''

	user_id = ''
	order_id = 1

	status = 'creating' # client: creating, validate, validated, rejected, prepayed
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
	plastic_color = ''
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
	
	price_estimate = 0.0
	price = 0.0
	prepayed = 0.0
	prepayment_percent = 0.3
	pay_code = 0

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

	def get_next_free_id(self, list):
		ids = []
		for elem in list:
			ids.append(int(elem.order_id))
		ids.sort()
		id = 1
		for elem in ids:
			if elem == id:
				id += 1
			else:
				break
		return id

	# def tell_designer(self):
	# 	for chat in self.app.chats:
	# 		if chat.is_employee and chat.user.role == 'Дизайнер' and chat.user.active:
	# 			text = 'Поступил заказ на оценку. Возьмете в работу?'
	# 			bts = [['Да, возьму', 'assign_order,yes,' + str(self.order_id)], ['Нет, оставлю другому', 'assign_order,no,' + str(self.order_id)]]
	# 			self.messages.append(self.GUI.tell_buttons_id(chat.user_id, text, bts, []))

	# def assign_designer(self, id):
	# 	if self.assinged_designer_id != '':
	# 		return False
	# 	self.assinged_designer_id = id
	# 	# self.db.order_assign_designer(self.order_id, id)
	# 	self.GUI.remove_messages(self.messages.copy())
	# 	self.messages = []
	# 	return True

	# def remove_designer_query(self, id):
	# 	for message in self.messages:
	# 		if message.chat_id == id:
	# 			self.GUI.remove_message(message)

	def set_plastic_type(self, type):
		self.plastic_type = type

	def set_plastic_color(self, color):
		self.plastic_color = color

	def set_layer_hight(self, height):
		self.layer_hight = layer_hight

	def set_priority(self, priority):
		self.priority = priority

	def set_quantity(self, quantity):
		self.quantity = quantity

	def set_time_estimate(self, time):
		start_time_estimate = ''
		end_time_estimate = ''

	def set_price_estimate(self, price):
		self.price_estimate = price

	def set_price(self, price):
		self.price = price