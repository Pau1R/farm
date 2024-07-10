from lib.employee.Owner import Owner
from lib.employee.Admin import Admin
from lib.employee.Operator import Operator
from lib.employee.designer.Designer import Designer
from lib.employee.Delivery import Delivery
from lib.Gui import Gui

from telebot import types as tbot

class Employee:
	address = '1'

	role = ''
	last_data = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.messages = []
		self.message = None
		self.roles = []
		self.GUI = Gui(app, chat, self.address)
		self.owner = Owner(app, chat, self.address + '/1')
		self.admin = Admin(app, chat, self.address + '/2')
		self.operator = Operator(app, chat, self.address + '/3')
		self.designer = Designer(app, chat, self.address + '/4')
		self.delivery = Delivery(app, chat, self.address + '/5')

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		if message.text == '/start':
			self.last_data = ''
			if len(self.roles) > 1:
				self.GUI.tell_buttons('Выберите роль:', self.roles.copy(), [], 1, 0)
			elif len(self.roles) == 1:
				message.btn_data = self.roles[0]
				self.send_first_message(message)
			else:
				self.GUI.tell('Вам не назначена роль')

		elif message.data_special_format:
			if message.file2 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.send_first_message(message)
			else:
				self.send_new_message(message)
		self.chat.add_if_text(self)

	def send_first_message(self, message):
		employee = None
		role = message.btn_data
		if role == 'Владелец' in self.roles:
			employee = self.owner
		elif role == 'Администратор' in self.roles:
			employee = self.admin
		elif role == 'Оператор' in self.roles:
			employee = self.operator
		elif role == 'Дизайнер' in self.roles:
			employee = self.designer
		elif role == 'Выдача' in self.roles:
			employee = self.delivery

		self.role == role
		if employee != None:
			employee.last_data = ''
			employee.first_message(message)

	def send_new_message(self, message):
		if message.file2 == '1':
			self.role = 'Владелец'
			self.owner.new_message(message)
		elif message.file2 == '2':
			self.role = 'Администратор'
			self.admin.new_message(message)
		elif message.file2 == '3':
			self.role = 'Оператор'
			self.operator.new_message(message)
		elif message.file2 == '4':
			self.role = 'Дизайнер'
			self.designer.new_message(message)
		elif message.file2 == '5':
			self.role = 'Выдача'
			self.delivery.new_message(message)