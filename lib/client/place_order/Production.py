import sys
from datetime import datetime
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
	plastic_type = ''
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

		data = message.data
		function = message.function
		if message.data_special_format and (data == '' or data != self.last_data):
			self.last_data = data
			if function == '1':
				self.process_top_menu()
			elif function == '2':
				self.process_weight()
			elif function == '3':
				self.process_quantity()
			elif function == '4':
				self.process_type()
			elif function == '5':
				self.process_color()
			elif function == '6':
				self.process_name()
			elif function == '7':
				self.process_comment()
			elif function == '8':
				self.process_confirmation()
		if message.type in ['text','document']:
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'У вас есть готовый 3д файл?'
		buttons = ['Да', ['Нет, нужно разработать', 'no']]
		self.GUI.tell_buttons(text, buttons, buttons, 1, self.order.id)

	def show_weight(self):
		self.chat.set_context(self.address, 2)
		self.GUI.tell('Напишите приблизительно вес единицы изделия в граммах')

	def show_quantity(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Напишите сколько экземпляров вам нужно')
		
	def show_type(self):
		self.chat.set_context(self.address, 4)
		text = 'Напишите тип материала'
		buttons = [['Тип материала не важен', 'any']]
		buttons.append(['Не знаю какой нужен','any'])
		self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.id)
		
	def show_color(self):
		self.chat.set_context(self.address, 5)
		self.GUI.tell('Напишите цвет')

	def show_name(self):
		self.chat.set_context(self.address, 6)
		self.GUI.tell('Напишите название для вашего заказа')

	def show_comment(self):
		self.chat.set_context(self.address, 7)
		buttons = [['Комментариев к заказу не имею', 'none']]
		self.GUI.tell_buttons('Напишите комментарий', buttons, [], 7, self.order.id)

	def show_confirmation(self):
		text = 'Подтвердите создание заказа'
		buttons = [['Подтверждаю', 'confirm'], ['Удалить заказ', 'remove']]
		self.GUI.tell_buttons(text, buttons, buttons, 8, self.order.id)

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
			self.show_quantity()
		except:
			self.show_weight()

	def process_quantity(self):
		self.chat.context = ''
		try:
			self.order.quantity = int(self.message.text)
			self.show_type()
		except:
			self.show_quantity()

	def process_type(self):
		self.plastic_type = self.message.text
		if self.message.btn_data == 'any':
			self.plastic_type = 'любой'
		self.show_color()

	def process_color(self):
		self.color = self.message.text
		self.show_name()

	def process_name(self):
		self.chat.context = ''
		self.order.name = self.message.text
		self.show_comment()

	def process_comment(self):
		self.chat.context = ''
		if self.message.btn_data != 'none':
			self.order.comment = self.message.text
		else:
			self.order.comment = ''
		self.show_confirmation()

	def process_confirmation(self):
		data = self.message.btn_data
		if data == 'confirm':
			self.order.quality = f'Цвет: {self.color}'  # misuse of order.quality field, may cause errors in the future
			if self.need_design:
				self.order.quality += '\nТребуется 3д дизайн'
			self.order.weight = self.weight
			self.order.plastic_type = self.plastic_type
			self.order.plastic_type = self.plastic_type
			self.order.date = datetime.today()
			self.order.logical_status = 'validate'
			self.order.user_id = self.app.chat.user_id
			self.app.orders_append(self.order)
			self.app.db.create_order(self.order)
			self.chat.user.show_wait_for_designer()
			for chat in self.app.chats:
				if chat.is_employee and 'Дизайнер' in chat.user.roles:
					chat.user.designer.validate.show_new_order(self.order)
		self.chat.user.reset_order()
		self.chat.user.show_top_menu()