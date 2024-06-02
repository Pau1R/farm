import sys
import time
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.Texts import Texts

class Delivery:
	address = ''

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''
	texts = None

	order = ''
	price = 0

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		self.GUI.clear_order_chat(message.instance_id)

		if message.data_special_format:
			if message.file3 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.process_top_menu()
				if message.function == '2':
					self.process_order_query()
				if message.function == '3':
					self.process_issue_order()
				if message.function == '4':
					self.process_pay_for_order()
			# elif message.file3 == '1':
			# 	self.sub_something.new_message(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = f'Здравствуйте, {self.chat.user_name}. Для выдачи заказа нажмите на кнопку'
		buttons = ['Выдать заказ']
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_order_query(self):
		self.chat.set_context(self.address, 2)
		self.GUI.tell('Введите код получения заказа который сообщит вам клиент')

	def show_client(self):
		if self.order.is_payed():
			text = f'Выдайте заказ № {self.order.id}\n'
			buttons = [['Клиент забрал заказ', 'issued']]
		else:
			text = f'Предоставьте заказ № {self.order.id} клиенту для ознакомления.\n'
			text += f'Заказ оплачен не полностью. Сумма доплаты: {self.order.remaining_payment()} рублей\n\n'
			text += 'Клиент может оплатить наличными либо переводом через чат-бот на странице заказа.'
			buttons = [['Клиент оплатил наличными', 'payed']]
			buttons.append(['Клиент отказался от заказа', 'refused'])
		self.GUI.tell_buttons(text, buttons, buttons, 3, self.order.id)

	def show_order_payed(self, order):
		text = f'Заказ № {self.order.id} оплачен полностью'
		buttons = [['Клиент забрал заказ', 'issued']]
		message = self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.id)
		message.general_clear = False

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		if data == 'Выдать заказ':
			self.show_order_query()

	def process_order_query(self):
		code = self.message.text
		order = self.app.order_logic.get_order_by_delivery_code(code)
		self.order = order
		order.delivery_user_id = self.chat.user_id
		self.show_client()

	def process_client(self):
		data = self.message.btn_data
		if data == 'issued' or data == 'payed':
			self.order_issued(self.order)
		elif data == 'refused':
			self.order.status = 'client_refused' # client doesn't get refund for prepayment
			self.show_top_menu()

	def process_order_payed(self):
		if self.message.btn_data == 'issued':
			order = self.app.order_logic.get_order_by_id(self.message.instance_id)
			self.order_issued(order)

#---------------------------- LOGIC ----------------------------

	def order_issued(self, order):
		self.order.status = 'issued'
		time.sleep(5)
		self.show_top_menu()