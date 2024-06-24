import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Production:
	address = ''

	app = None
	chat = None
	order = None
	GUI = None

	need_design = False
	weight = 0
	type_ = ''
	color = ''

	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.order = self.chat.user.order
		self.need_design = False
		self.weight = 0
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
			elif message.function == '2':
				self.process_weight()
			elif message.function == '3':
				self.process_type()
			elif message.function == '4':
				self.process_color()
			elif message.function == '5':
				self.process_confirmation()
		if message.type == 'text' or self.message.type == 'document':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'У вас есть готовый 3д файл?'
		buttons = ['Да', ['Нет, нужно разработать', 'no']]
		self.GUI.tell_buttons(text, buttons, buttons, 1, self.order.id)

	def show_weight(self):
		self.chat.set_context(self.address, 2)
		self.GUI.tell('Напишите общий вес в килограммах')
		
	def show_type(self):
		self.chat.set_context(self.address, 3)
		text = 'Напишите тип материала'
		buttons = [['Тип материала не важен', 'any']]
		self.GUI.tell_buttons(text, buttons, buttons, 3, self.order.id)
		
	def show_color(self):
		self.chat.set_context(self.address, 4)
		self.GUI.tell('Напишите цвет')

	def show_confirmation(self):
		text = 'Подтвердите создание заказа'
		buttons = [['Подтверждаю', 'confirm'], ['Удалить заказ', 'remove']]
		self.GUI.tell_buttons(text, buttons, buttons, 5, self.order.id)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Да':
			self.need_design = False
		self.show_weight()

	def process_weight(self):
		self.chat.context = ''
		try:
			self.weight = int(self.message.text)
			self.show_type()
		except:
			self.show_weight()

	def process_type(self):
		self.type_ = self.message.text
		if self.message.btn_data == 'any':
			self.type_ = 'любой'
		self.show_color()

	def process_color(self):
		self.color = self.message.text
		self.show_confirmation()

	def process_confirmation(self):
		data = self.message.btn_data
		if data == 'confirm':
			x = ''
			# TODO: think over functionality
		self.chat.user.reset_order()
		self.chat.user.show_top_menu()