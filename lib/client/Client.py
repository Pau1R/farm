import sys
import random
import time
from datetime import date
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.order.GUI import Client_order
from lib.client.Info import Info

from lib.client.place_order.Article import Farm_model
from lib.client.place_order.Stl import Their_model
from lib.client.place_order.Link import Internet_model
from lib.client.place_order.Sketch import Their_sketch
from lib.client.place_order.Item import Their_item
from lib.client.place_order.Production import Production

class Client:
	address = '1'

	app = None
	chat = None
	order = None
	name = ''

	GUI = None
	message = None

	last_data = ''
	
	menu = None
	their_model = None
	client_order = None

	payId = ''
	money_payed = 0.0
	orders_canceled = 0
	limit_date = date.today()

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.reset_order()

		self.client_order = Client_order(app, chat, self.address + '/1')
		self.info = Info(app, chat, self.address + '/2')

		self.farm_model = Farm_model(app, chat, self.address + '/3')
		self.their_model = Their_model(app, chat, self.address + '/4')
		self.internet_model = Internet_model(app, chat, self.address + '/5')
		self.their_sketch = Their_sketch(app, chat, self.address + '/6')
		self.their_item = Their_item(app, chat, self.address + '/7')
		self.production = Production(app, chat, self.address + '/8')

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.text == '/start':
			self.last_data = ''
			self.reset_order()
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
				self.client_order.new_message(message)
			elif message.file2 == '2':
				self.info.new_message(message)
			elif message.file2 == '3':
				self.farm_model.new_message(message)
			elif message.file2 == '4':
				self.their_model.new_message(message)
			elif message.file2 == '5':
				self.internet_model.new_message(message)
			elif message.file2 == '6':
				self.their_sketch.new_message(message)
			elif message.file2 == '7':
				self.their_item.new_message(message)
			elif message.file2 == '8':
				self.production.new_message(message)
		if message.type == 'text' and message.file2 == '' and message.text != '/start':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.context = 'secret_message~' + self.address + '|1||'
		buttons = [['Сделать заказ', 'order'], ['Информация о студии', 'info']]
		if len(self.get_orders(['validate', 'validated', 'prepayed'])) > 0:
			buttons.insert(1, ['Мои заказы', 'orders'])
		self.GUI.tell_buttons('Выберите действие', buttons, buttons, 1, 0)

	def show_order_menu(self):
		buttons = []
		# buttons.append(['Ввести артикул из каталога str3d.ru', 'farm model'])
		buttons.append(['Распечатать ваш файл', 'user model'])
		buttons.append(['Распечатать модель по ссылке из интернета', 'internet model'])
		buttons.append(['Создать и распечатать модель по вашему чертежу', 'sketch'])
		buttons.append(['Создать копию вашего предмета', 'user item'])
		buttons.append(['Мелкосерийное производство', 'production'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите тип заказа', buttons, [], 2, 0)

	def show_orders(self):
		text = 'Мои заказы'
		buttons = []
		x = 1
		orders = self.get_orders(['validate', 'validated', 'prepayed'])
		orders.sort(key=self.get_object_date)
		for order in orders:
			buttons.append([order.name, order.id])
		if not buttons:
			self.show_top_menu()
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
			self.farm_model.first_message(self.message)
		elif self.message.btn_data == 'user model':
			self.their_model.first_message(self.message)
		elif self.message.btn_data == 'internet model':
			self.internet_model.first_message(self.message)
		elif self.message.btn_data == 'sketch':
			self.their_sketch.first_message(self.message)
		elif self.message.btn_data == 'user item':
			self.their_item.first_message(self.message)
		elif self.message.btn_data == 'production':
			self.production.first_message(self.message)
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
		self.app.db.update_chat(self.chat)

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

	def reset_order(self):
		self.order = Order(self.app, 0)