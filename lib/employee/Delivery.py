import sys
import time
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.Texts import Texts

class Delivery:
	address = '1/5'

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''
	texts = None

	order = ''
	price = 0

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address)

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
		buttons = ['Выдать заказ']
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(self.texts.delivery_top_menu(self.chat.user.name), buttons, ['Назад'], 1, 0)

	def show_order_query(self):
		self.chat.set_context(self.address, 2)
		self.GUI.tell('Введите код получения заказа')

	def show_issue_order(self):
		buttons = ['Заказ выдан']
		self.GUI.tell_buttons(self.texts.delivery_issue_order(self.order), buttons, [], 3, 0)

	def show_pay_for_order(self):
		buttons = ['Наличные приняты']
		self.GUI.tell_buttons(self.texts.delivery_pay_for_order(self.order, self.price), buttons, [], 4, 0)

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		if self.message.btn_data == 'Выдать заказ':
			self.show_order_query()

	def process_order_query(self):
		code = self.message.text # order recieving code
		self.order = 5 # TODO: get order number from receiving code
		self.price = 1000 # TODO: get order price
		if self.price > 0: # if order is not paid
			self.show_pay_for_order()
		else:
			self.show_issue_order()

	def process_issue_order(self):
		if self.message.btn_data == 'Заказ выдан':
			self.GUI.tell_permanent(f'Заказ {self.order} выдан')
			time.sleep(3)
			self.show_top_menu()
			# change order status to received

	def process_pay_for_order(self):
		if self.message.btn_data == 'Наличные приняты':
			self.show_issue_order()