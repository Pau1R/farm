import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Operator:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.message = None
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		function = message.function
		if message.data_special_format:
			if self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'Здравствуйте, ' + self.chat.user_name

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.data == 'Сотрудники':
			print('hi')
			# self.show_employees()