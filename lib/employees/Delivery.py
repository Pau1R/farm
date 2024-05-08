import sys
import time
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.Texts import Texts

class Delivery:
	app = None
	chat = None
	GUI = None
	message = None
	context = ''
	texts = Texts()

	order = ''
	price = 0

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
		elif context == 'top_menu':
			self.process_top_menu()
		elif context == 'order_query':
			self.process_order_query()
		elif context == 'issue_order':
			self.process_issue_order()
		elif context == 'pay_for_order':
			self.process_pay_for_order()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		buttons = ['Выдать заказ']
		self.GUI.tell_buttons(self.texts.delivery_top_menu(self.chat.user.name), buttons, [])

	def show_order_query(self):
		self.context = 'order_query'
		self.GUI.tell('Введите код получения заказа')

	def show_issue_order(self):
		self.context = 'issue_order'
		buttons = ['Заказ выдан']
		self.GUI.tell_buttons(self.texts.delivery_issue_order(self.order), buttons, [])

	def show_pay_for_order(self):
		self.context = 'pay_for_order'
		buttons = ['Наличные приняты']
		self.GUI.tell_buttons(self.texts.delivery_pay_for_order(self.order, self.price), buttons, [])

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Выдать заказ':
			self.show_order_query()

	def process_order_query(self):
		self.context = ''
		code = self.message.data # order recieving code
		self.order = 5 # TODO: get order number from receiving code
		self.price = 1000 # TODO: get order price
		if self.price > 0: # if order is not paid
			self.show_pay_for_order()
		else:
			self.show_issue_order()

	def process_issue_order(self):
		self.context = ''
		if self.message.data == 'Заказ выдан':
			self.GUI.tell_permanent(f'Заказ {self.order} выдан')
			time.sleep(3)
			self.show_top_menu()
			# change order status to received

	def process_pay_for_order(self):
		self.context = ''
		if self.message.data == 'Наличные приняты':
			self.show_issue_order()