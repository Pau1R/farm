import sys
from datetime import datetime
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
import time

class Link:
	address = ''

	app = None
	chat = None
	order = None
	GUI = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.order = self.chat.user.order
		self.show_link()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_link()
			elif message.function == '2':
				self.process_quantity()
			elif message.function == '3':
				self.process_quality()
			elif message.function == '4':
				self.process_name()
			elif message.function == '5':
				self.process_comment()
			elif message.function == '6':
				self.process_confirmation()

		if message.type == 'text' or self.message.type == 'document':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_link(self):
		self.chat.set_context(self.address, 1)
		self.GUI.tell('Отправьте ссылку на модель из интернета')

	def show_quantity(self):
		text = 'Сколько экземпляров вам нужно?'
		buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
		self.GUI.tell_buttons(text, buttons, ['1', '2'], 2, self.order.id)

	def show_quality(self):
		text = 'Какое качество печати вам нужно?'
		buttons = [['максимально дешевое', 'cheap'], ['оптимальное цена/качество','optimal'], ['максимальное качество', 'quality'], ['максимальная прочность', 'durability']]
		self.GUI.tell_buttons(text, buttons, [], 3, self.order.id)

	def show_name(self):
		self.chat.set_context(self.address, 4)
		self.GUI.tell('Напишите название вашего заказа')

	def show_comment(self):
		self.chat.set_context(self.address, 5)
		buttons = ['Комментариев к заказу не имею']
		self.GUI.tell_buttons('Напишите комментарий', buttons, [], 5, self.order.id)

	def show_confirmation(self):
		text = 'Подтвердите создание заказа'
		buttons = [['Подтверждаю', 'confirm'], ['Удалить заказ', 'remove']]
		self.GUI.tell_buttons(text, buttons, buttons, 6, self.order.id)

#---------------------------- PROCESS ----------------------------

	def process_link(self):
		self.order.link = self.message.text
		self.show_quantity()

	def process_quantity(self):
		try:
			self.order.quantity = int(self.message.btn_data)
			self.show_quality()
		except:
			self.show_quantity()

	def process_quality(self):
		if self.message.btn_data == '':
			self.show_quality()
		self.order.quality = self.message.btn_data
		self.show_name()

	def process_name(self):
		self.order.name = self.message.text
		self.show_comment()

	def process_comment(self):
		self.chat.context = ''
		if self.message.btn_data != 'Комментариев к заказу не имею':
			self.order.comment = self.message.text
		self.show_confirmation()

	def process_confirmation(self):
		data = self.message.btn_data
		if data == 'confirm':
			self.order.date = datetime.today()
			# self.order.physical_status = 'preparing'
			self.order.logical_status = 'validate'
			self.order.user_id = self.app.chat.user_id
			self.app.orders_append(self.order)
			self.app.db.create_order(self.order)
			self.chat.user.show_wait_for_designer()
			for chat in self.app.chats:
				if chat.is_employee and 'Дизайнер' in chat.user.roles:
					chat.user.designer.link.show_new_order(self.order)
		self.chat.user.reset_order()
		self.chat.user.show_top_menu()