import sys
import random
import time
from datetime import date
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts
from lib.client.Order import Order
from lib.client.Client_model import Client_model
from lib.client.Client_color import Client_color
from lib.client.Client_order import Client_order
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
	client_color = None
	client_order = None
	order_id = None

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

		self.client_model = Client_model(app, chat)
		self.client_color = Client_color(app, chat)
		self.client_order = Client_order(app, chat, '1/3') # TODO: consider moving address to this format for all subfiles 
		self.info = Info(app, chat)

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
				elif message.function == '7': # TODO: move info menu into different file
					self.process_info()
				elif message.function == '8':
					self.process_receive()
				elif message.function == '9':
					self.process_tech()
				elif message.function == '10':
					self.process_disclaimer()
				elif message.function == '11':
					self.process_support()
			elif message.file2 == '1':
				self.client_model.new_message(message)
			elif message.file2 == '2':
				self.client_color.new_message(message)
			elif message.file2 == '3':
				self.client_order.new_message(message)
			elif message.file2 == '4':
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
			buttons.append([order.name, order.order_id])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 5, 0)

	def show_info(self):
		text = 'Информация о студии'
		buttons = []
		buttons.append(['Доступные цвета и типы пластика', 'colors'])
		buttons.append(['Получение заказов', 'receive'])
		buttons.append(['Технические подробности', 'tech'])
		buttons.append(['Дисклеймер', 'disclaimer'])
		buttons.append(['Поддержка', 'support'])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 7, 0)

	def show_receive(self):
		text = 'Среднее время выполнения заказа: 2-3 дня\n\n'
		text += 'Пункт выдачи: г. Стерлитамак, ул. Сакко и Ванцетти, 63, "Бизнес-контакт". График работы: ежедневно с 9:00 до 21:00.\n\n'
		text += 'Доставка по странам СНГ службой boxberry за счет клиента'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 8, 0)

	def show_tech(self):
		text = 'Технология печати: одноцветная на fdm принтерах.\n\n'
		text += 'Используемые принтеры: BAMBU LAB P1S и CREALITY ENDER 3 S1 PRO.\n\n'
		text += 'Есть ограниченная возможность печатать поликарбонатом'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 9, 0)

	def show_disclaimer(self):
		text = """
Дисклеймер:
1) не даю гарантии на изделие
2) не несу ответственности за причиненный изделием вред
3) Если вес одного изделия превышает 0.8 кг, то могут быть отличия в цвете
3) Если общий вес нескольких изделий заказа превышает 0.8 кг, то также могут быть отличия в цвете"""
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 10, 0)

	def show_support(self):
		self.chat.set_context(self.address, 11)
		text = 'Опишите вашу проблему'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 11, 0)

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
		data = self.message.btn_data
		if data == 'Назад':
			self.show_top_menu()
		elif data == 'colors':
			self.client_color.last_data = ''
			self.client_color.first_message(self.message)
		elif data == 'receive':
			self.show_receive()
		elif data == 'tech':
			self.show_tech()
		elif data == 'disclaimer':
			self.show_disclaimer()
		elif data == 'support':
			self.show_support()

	def process_receive(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_info()

	def process_tech(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_info()

	def process_disclaimer(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_info()

	def process_support(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.chat.context = ''
		else: # TODO: think over the support logic
			text = self.message.text
			self.GUI.tell('Ваш обращение получено, ждите ответа')
			time.sleep(2)
		self.show_info()

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
		return object.date

	def penalty(self):
		self.orders_canceled += 1
		if self.orders_canceled >= 3:
			self.limit_date = date.today()

	def is_limited(self):
		if self.orders_canceled >= 3:  # repeated order cancelation limit
			period = (date.today() - self.limit_date).days
			if period > 1:  # days to limit placing orders
				self.orders_canceled -= 1 # give one chance to place order
			else:
				return True
		return False

	# TODO: limit amount of unpaid orders