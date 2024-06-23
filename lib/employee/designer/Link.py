import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order

class Link:
	address = ''

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''

	order = None
	
	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.context = ''
		text = self.texts.designer_orders_validate_text(self.order_timer, self.app.orders)
		
		buttons = self.texts.designer_orders_validate_btns(self.app.orders, self.app.chat)
		if not buttons:
			self.app.chat.user.designer.first_message(self.message)
		buttons.extend(['Назад'])
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.app.chat.user.designer.first_message(self.message)
		else:
			for order in self.app.orders:
				if order.id == int(self.message.btn_data):
					self.order = order
					self.show_validate()
