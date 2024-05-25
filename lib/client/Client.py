import sys
import random
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts
from lib.client.Order import Order
from lib.client.Client_model import Client_model
from lib.client.Client_color import Client_color
from lib.client.Client_order import Client_order

class Client:
	address = '1'

	app = None
	chat = None
	order = None
	name = ''
	date = None
	GUI = None
	message = None
	texts = None

	last_data = ''
	
	menu = None
	client_model = None
	client_color = None
	client_order = None
	order_id = None

	payId = ''
	money_payed = 0.0

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.texts = Texts(app)
		self.GUI = Gui(app, chat, self.address)

		self.order = Order(app, 1)
		self.app.orders.append(self.order)

		self.client_model = Client_model(app, chat)
		self.client_color = Client_color(app, chat)
		self.client_order = Client_order(app, chat, '1/4')

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
				# elif message.function == '3':
					# self.process_supports()
				elif message.function == '4':
					self.process_price()
				elif message.function == '5':
					self.process_orders()
				elif message.function == '6':
					self.process_order()
				elif message.function == '7':
					self.process_info()
			elif message.file2 == '1':
				self.client_model.new_message(message)
			elif message.file2 == '2':
				self.client_color.new_message(message)
			elif message.file2 == '4':
				self.client_order.new_message(message)
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
			buttons.append([order.name, order.order_id])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 5, 0)

	def show_info(self):
		buttons = [['Доступные цвета и типы пластика', 'colors'], 'Назад']
		self.GUI.tell_buttons(self.texts.info_text, buttons, buttons, 7, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.chat.context = ''
		if self.message.text == 'я_хочу_стать_сотрудником':
			self.chat.get_employed = True
			self.GUI.tell('Ждите подтверждения')
		elif self.message.btn_data == 'order':
			self.show_order_menu()
		elif self.message.btn_data == 'info':
			self.show_info()
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

	def process_info(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		elif self.message.btn_data == 'colors':
			self.client_color.last_data = ''
			self.client_color.first_message(self.message)

#---------------------------- LOGIC ----------------------------

	def get_order(self, order_id):
		for order in self.app.orders:
			if order.order_id == order_id:
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
		return object.created