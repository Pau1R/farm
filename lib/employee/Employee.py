from lib.employee.Owner import Owner
from lib.employee.Admin import Admin
from lib.employee.Operator import Operator
from lib.employee.Designer import Designer
from lib.employee.Delivery import Delivery
from lib.Gui import Gui

from telebot import types as tbot

class Employee:
	address = '1'

	app = None
	chat = None
	GUI = None

	messages = []
	message = None
	roles = []
	name = ''
	date = None
	active = True
	
	last_data = ''

	employee = None
	owner = None
	admin = None
	operator = None
	designer = None
	delivery = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.owner = Owner(app, chat)
		self.admin = Admin(app, chat)
		self.operator = Operator(app, chat)
		self.designer = Designer(app, chat)
		self.delivery = Delivery(app, chat)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		if message.text == '/start':
			self.last_data = ''
			if len(self.roles) > 1:
				self.GUI.tell_buttons('Выберите роль:', self.roles.copy(), [], 1, 0)
			elif len(self.roles) == 1:
				self.send_first_message(message)
			else:
				self.GUI.tell('Вам не назначена роль')

		# elif message.data.split(",")[0] == 'assign_order':
		# 	self.process_assign_order()

		elif message.data_special_format:
			if message.file2 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.send_first_message(message)
			else: # pass message to child class
				self.send_new_message(message)
		if message.type == 'text' and message.text != '/start':
			self.GUI.messages_append(message)

	def send_first_message(self, message):
		role = message.btn_data
		if role == 'Владелец' in self.roles:
			self.owner.first_message(message)
		elif role == 'Администратор' in self.roles:
			self.admin.first_message(message)
		elif role == 'Оператор' in self.roles:
			self.operator.first_message(message)
		elif role == 'Дизайнер' in self.roles:
			self.designer.first_message(message)
		elif role == 'Выдача' in self.roles:
			self.delivery.first_message(message)

	def send_new_message(self, message):
		if message.file2 == '1':
			self.owner.new_message(message)
		elif message.file2 == '2':
			self.admin.new_message(message)
		elif message.file2 == '3':
			self.operator.new_message(message)
		elif message.file2 == '4':
			self.designer.new_message(message)
		elif message.file2 == '5':
			self.delivery.new_message(message)

	# def process_assign_order(self):
	# 	id = int(self.message.data.split(",")[-1])
	# 	print(id)
	# 	# print('process_assign_order')
	# 	for order in self.app.orders:
	# 		print('order', order.order_id, type(order.order_id), id, type(id))
	# 		if order.order_id == id:
	# 			print(self.message.data.split(",")[1])
	# 			if self.message.data.split(",")[1] == 'yes':
	# 				if not order.assign_designer(self.chat.user_id):
	# 					self.GUI.tell('Заказ назначен кому-то другому')
	# 			else:
	# 				# print('process_assign_order remove')
	# 				order.remove_designer_query(self.chat.user_id)