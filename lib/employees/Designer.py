import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.clients.Order import Order
from lib.Texts import Texts
from lib.employees.Designer_validate import Validate

class Designer:
	app = None
	chat = None
	GUI = None
	texts = None
	message = None
	context = ''

	menu = None
	validate = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat)
		self.texts = Texts()
		self.validate = Validate(app, chat)

	def first_message(self, message):
		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		context = self.context

		if self.menu == self.validate:
			self.menu.new_message(message)
		else:
			self.GUI.messages.append(message)
			if context == 'first_message':
				self.show_top_menu()
			elif context == 'top_menu':
				self.process_top_menu()
			elif context == 'orders_design':
				self.process_orders_design()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		self.GUI.tell_buttons(self.texts.designer_top_menu_text(self.chat.user.name, len(self.app.orders)), self.texts.designer_top_menu_btns, [])

	def show_orders_design(self):
		self.context = 'orders_design'
		self.GUI.tell_buttons(self.texts.designer_orders_design_text(self.order_timer, self.app.orders), self.texts.designer_orders_design_btns(self.order), ['Назад'])

	def show_order(self):
		self.context = 'order'
		self.GUI.tell_buttons(self.texts.designer_order_text(self.order), self.texts.designer_order_btns(self.order_timer, self.order), ['Назад'])
		
	def show_finished_orders(self):
		self.context = 'finished_orders'
		buttons = []
		buttons.extend(['Назад'])
		self.GUI.tell_buttons('', buttons, ['Назад'])

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'design':
			self.show_orders_design()
		if self.message.data == 'validate':
			self.menu = self.validate
			self.validate.first_message(self.message)
		if self.message.data == 'parametric':
			self.show_orders_parametric()
		if self.message.data == 'finished':
			self.show_finished_orders()

	def process_orders_design(self):
		self.context = ''
		if self.message.data == 'Назад':
			self.show_top_menu()
		for order in self.app.orders:
			if self.message.data.split(":")[0] == order.order_id:
				self.order = order
				self.show_order()

	def process_finished_orders(self):
		self.context = ''
		if self.message.data == 'Назад':
			self.show_top_menu()