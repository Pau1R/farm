import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Operator:
	address = ''

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format:
			if message.file3 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.process_top_menu()
				# if message.function == '2':
				# 	self.process_orders_design()
			# elif message.file3 == '1':
			# 	self.sub_something.new_message(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'Здравствуйте, ' + self.chat.user_name

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.data == 'Сотрудники':
			print('hi')
			# self.show_employees()