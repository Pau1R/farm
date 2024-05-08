from lib.employees.Owner import Owner
from lib.employees.Admin import Admin
from lib.employees.Operator import Operator
from lib.employees.Designer import Designer
from lib.employees.Delivery import Delivery
from lib.Gui import Gui

from telebot import types as tbot

class Employee:
	app = None
	chat = None
	GUI = None

	messages = []
	message = None
	roles = []
	role = ''
	name = ''
	date = None
	active = True
	
	context = ''

	employee = None
	owner = None
	admin = None
	operator = None
	designer = None
	delivery = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		if message.text == '/start':
			if len(self.roles) > 1:
				self.context = 'select_role'
				self.GUI.tell_buttons('Выберите роль:', self.roles.copy(), [])
			elif len(self.roles) == 1:
				if self.set_role(self.roles[0]):
					self.employee.first_message(message)
			else:
				self.GUI.tell('Вам не назначена роль')

		elif message.data.split(",")[0] == 'assign_order':
			self.process_assign_order()

		elif self.context == 'select_role':
			self.context = ''
			if self.set_role(message.data):
				self.employee.first_message(message)

		elif self.employee != None:
			self.employee.new_message(message)

	def set_role(self, role):
		if role == 'Владелец' in self.roles:
			if self.owner == None:
				self.owner = Owner(self.app, self.chat)
			self.employee = self.owner
			self.role = 'Владелец'
		elif role == 'Администратор' in self.roles:
			if self.admin == None:
				self.admin = Admin(self.app, self.chat)
			self.employee = self.admin
			self.role = 'Администратор'
		elif role == 'Оператор' in self.roles:
			if self.operator == None:
				self.operator = Operator(self.app, self.chat)
			self.employee = self.operator
			self.role = 'Оператор'
		elif role == 'Дизайнер' in self.roles:
			if self.designer == None:
				self.designer = Designer(self.app, self.chat)
			self.employee = self.designer
			self.role = 'Дизайнер'
		elif role == 'Выдача' in self.roles:
			if self.delivery == None:
				self.delivery = Delivery(self.app, self.chat)
			self.employee = self.delivery
			self.role = 'Выдача'
		else:
			self.role = ''
			self.employee = None
			return False
		return True

	def process_assign_order(self):
		id = int(self.message.data.split(",")[-1])
		print(id)
		# print('process_assign_order')
		for order in self.app.orders:
			print('order', order.order_id, type(order.order_id), id, type(id))
			if order.order_id == id:
				print(self.message.data.split(",")[1])
				if self.message.data.split(",")[1] == 'yes':
					if not order.assign_designer(self.chat.user_id):
						self.GUI.tell('Заказ назначен кому-то другому')
				else:
					# print('process_assign_order remove')
					order.remove_designer_query(self.chat.user_id)