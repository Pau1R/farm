import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Operator:
	app = None
	chat = None
	GUI = None
	message = None
	context = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat)

	def first_message(self, message):
		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.messages.append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_top_menu()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		text = 'Здравствуйте, ' + self.chat.name

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Сотрудники':
			print('hi')
			# self.show_employees()