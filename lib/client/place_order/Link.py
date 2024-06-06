import sys
from datetime import datetime
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
import time

class Internet_model:
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
		if self.chat.user.is_limited():
			self.show_limited()
		elif self.chat.user.is_unprepaided_orders_limit_reached():
			self.show_unprepaided_orders_limit_reached()
		else:
			self.show_name()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_name()
			elif message.function == '2':
				self.process_link()
		if message.type == 'text' or self.message.type == 'document':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_name(self):
		self.chat.set_context(self.address, 1)
		self.GUI.tell('Напишите название для вашего заказа')

	def show_link(self):
		self.chat.set_context(self.address, 2)
		self.GUI.tell('Отправьте ссылку на модель')

	def show_wait_for_designer(self):
		self.GUI.tell_permanent(f'Заказ {self.order.name} передан дизайнеру для оценки, ожидайте.')
		time.sleep(3)
		self.chat.user.show_top_menu()

	def show_limited(self):
		text = 'Вы слишком много раз отменили оцененные заказы, внесите предоплату за любой заказ либо подождите несколько дней.'
		text += ' Оценка производится вручную, а дизайнер ценит свое время.'
		self.GUI.tell(text)
		time.sleep(5)
		self.chat.user.show_top_menu()

	def show_unprepaided_orders_limit_reached(self):
		self.GUI.tell('У вас 3 непредоплаченных заказа, больше нельзя =)')
		time.sleep(5)
		self.chat.user.show_top_menu()

#---------------------------- PROCESS ----------------------------

	def process_name(self):
		self.order.name = self.message.text
		self.show_link()

	def process_link(self):
		self.order.link = self.message.text
		self.order.date = datetime.today()
		self.order.print_status = 'preparing'
		self.order.status = 'validate'
		self.order.user_id = self.app.chat.user_id
		# self.order.tell_designer()
		self.app.orders.append(self.order)
		self.app.db.create_order(self.order)
		self.show_wait_for_designer()
		for chat in self.app.chats:
			if chat.is_employee and 'Дизайнер' in chat.user.roles:
				chat.user.designer.validate.show_new_order(self.order)
		return

	# TODO: add order confirmation