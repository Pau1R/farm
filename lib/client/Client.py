import sys
import random
import time
from datetime import date
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts
from lib.order.Order import Order
from lib.client.Model import Client_model
from lib.client.Order import Client_order
from lib.client.Info import Info

class Client:
	address = '1'

	app = None
	chat = None
	order = None
	name = ''
	# date_ = None
	GUI = None
	message = None
	texts = None

	last_data = ''
	
	menu = None
	client_model = None
	client_order = None
	# order_id = None

	payId = ''
	money_payed = 0.0
	orders_canceled = 0
	limit_date = date.today()

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.texts = Texts(app)
		self.GUI = Gui(app, chat, self.address)
		self.order = Order(app, 1)

		self.client_model = Client_model(app, chat, self.address + '/1')
		self.client_order = Client_order(app, chat, self.address + '/2')
		self.info = Info(app, chat, self.address + '/3')

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.text == '/start':
			self.last_data = ''
			self.order.reset()
			self.show_top_menu()
		elif message.data_special_format:
			if message.file2 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.process_top_menu()
				if message.function == '2':
					self.process_order_menu()
				elif message.function == '4':
					self.process_price()
				elif message.function == '5':
					self.process_orders()
				elif message.function == '6':
					self.process_order()
			elif message.file2 == '1':
				self.client_model.new_message(message)
			elif message.file2 == '2':
				self.client_order.new_message(message)
			elif message.file2 == '3':
				self.info.new_message(message)
		if message.type == 'text' and message.file2 == '' and message.text != '/start':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.context = 'secret_message~' + self.address + '|1||'
		buttons = [['Сделать заказ', 'order'], ['Информация о студии', 'info']]
		if len(self.get_orders(['validate', 'validated', 'prepayed'])) > 0:
			buttons.insert(1, ['Мои заказы', 'orders'])
		self.GUI.tell_buttons(self.texts.top_menu, buttons, buttons, 1, 0)

	def show_order_menu(self):
		buttons = self.texts.order_buttons.copy()
		buttons.append('Назад')
		self.GUI.tell_buttons(self.texts.order_menu, buttons, [], 2, 0)

	def show_orders(self):
		text = 'Мои заказы'
		buttons = []
		x = 1
		orders = self.get_orders(['validate', 'validated', 'prepayed'])
		orders.sort(key=self.get_object_date)
		for order in orders:
			buttons.append([order.name, order.id])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 5, 0)

	def show_becomes_employee(self):
		self.GUI.tell('Вы стали сотрудником, поздравляем!')

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.chat.context = ''
		if self.message.text == 'я_хочу_стать_сотрудником':
			self.chat.get_employed = True
			self.GUI.tell('Ждите подтверждения')
		elif self.message.btn_data == 'order':
			self.show_order_menu()
		elif self.message.btn_data == 'info':
			self.info.first_message(self.message)
		elif self.message.btn_data == 'orders':
			self.show_orders()

	def process_order_menu(self):
		if self.message.btn_data == 'farm model':
			self.GUI.tell('Здесь будут находится готовые модели')
		elif self.message.btn_data == 'user model':
			self.client_model.first_message(self.message)
		elif self.message.btn_data == 'user drawing':
			self.GUI.tell('Здесь вы можете загрузить свои чертежы или рисунки для создания по ним 3д модели.')
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_orders(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		else:
			self.message.instance_id = int(self.message.btn_data)
			self.client_order.last_data = ''
			self.client_order.first_message(self.message)

#---------------------------- LOGIC ----------------------------

	def get_order(self, id):
		for order in self.app.orders:
			if order.id == id:
				return order
		return None

	def get_orders(self, statuses):
		orders = []
		for order in self.app.orders:
			if order.user_id == self.chat.user_id:
				if order.status == statuses or (statuses == [] or order.status in statuses):
					orders.append(order)
		return orders

	def get_object_date(self, object):
		return object.date

	def penalty(self):
		self.orders_canceled += 1
		if self.orders_canceled >= 3:
			self.limit_date = date.today()

	def is_limited(self):
		if self.orders_canceled >= 3:  # repeated order cancelation limit
			period = (date.today() - self.limit_date).days
			if period > 2:  # days to limit placing orders
				self.orders_canceled -= 1 # give one chance to place order
				self.limit_date = date.today()
			else:
				return True
		return False

	def is_unprepaided_orders_limit_reached(self):
		orders = self.app.order_logic.get_client_orders(self.chat.user_id)
		counter = 0
		for order in orders:
			if not order.is_prepayed():
				counter += 1
		if counter >= 3: # maximum allowed unprepaid orders
			return True
		return False
