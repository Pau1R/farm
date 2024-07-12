import sys
import random
import time
from datetime import date
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.order.GUI import Order_GUI
from lib.client.Info import Info

# from lib.client.place_order.Article import Farm_model
from lib.client.place_order.Stl_link import Stl_link
from lib.client.place_order.Sketch_item import Sketch_item
from lib.client.place_order.Production import Production

class Client:
	address = '1'

	last_data = ''
	
	payId = ''
	money_payed = 0.0
	orders_canceled = 0
	limit_date = date.today()

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.message = None
		self.order = None
		self.GUI = Gui(app, chat, self.address)
		self.reset_order()

		self.order_GUI = Order_GUI(app, chat, self.address + '/1')
		self.info = Info(app, chat, self.address + '/2')

		# self.farm_model = Farm_model(app, chat, self.address + '/3')
		self.stl_link = Stl_link(app, chat, self.address + '/4')
		self.sketch_item = Sketch_item(app, chat, self.address + '/5')
		self.production = Production(app, chat, self.address + '/6')

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		function = message.function
		file = self.chat.next_level_id(self)

		if message.text == '/start':
			self.last_data = ''
			self.reset_order()
			self.show_top_menu()
		elif message.data_special_format:
			if file == '1':
				self.order_GUI.new_message(message)
			elif file == '2':
				self.info.new_message(message)
			# elif file == '3':
			# 	self.farm_model.new_message(message)
			elif file == '4':
				self.stl_link.new_message(message)
			elif file == '5':
				self.sketch_item.new_message(message)
			elif file == '6':
				self.production.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				if function == '2':
					self.process_order_menu()
				elif function == '3':
					self.process_orders()
				elif function == '4':
					self.process_order_payed()
				elif function == '5':
					self.process_sketch_screenshots()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.context = 'secret_message~' + self.address + '|1||'
		buttons = [['Сделать заказ', 'order'], ['Информация о студии', 'info']]
		if len(self.app.order_logic.get_client_orders(self.chat.user_id)):
			buttons.insert(1, ['Мои заказы', 'orders'])
		self.GUI.tell_buttons('Выберите действие', buttons, buttons, 1, 0)

	def show_order_menu(self):
		if self.is_limited():
			self.last_data = ''
			self.show_limited()
			self.show_top_menu()
			return
		elif self.is_unprepaided_orders_limit_reached():
			self.last_data = ''
			self.show_unprepaided_orders_limit_reached()
			self.show_top_menu()
			return
		buttons = []
		# buttons.append(['Ввести артикул из каталога str3d.ru', 'farm model'])
		buttons.append(['stl файл', 'stl'])
		buttons.append(['Модель из интернета', 'link'])
		buttons.append(['Печать по чертежу', 'sketch'])
		buttons.append(['Копия предмета', 'item'])
		buttons.append(['Мелкосерийное производство (>10 единиц)', 'production'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите тип заказа', buttons, buttons, 2, 0)

	def show_orders(self):
		text = 'Мои заказы'
		buttons = []
		orders = self.app.order_logic.get_client_orders(self.chat.user_id)
		orders.sort(key=self.get_object_date)
		for order in orders:
			buttons.append([order.name, order.id])
		if not buttons:
			self.show_top_menu()
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 3, 0)

	def show_order_payed(self, order, amount):
		text = f'К заказу "{order.name}" поступил платеж в размере {amount} рублей'
		buttons = [['Перейти к заказу','show']]
		self.GUI.tell_buttons(text, buttons, buttons, 4, order.id)

	def show_sketch_screenshots(self, order):
		text = f'Модель к заказу "{order.name}" создана. Подтвердите соответствие модели чертежам.'
		buttons = [['Перейти к заказу','show']]
		self.GUI.tell_buttons(text, buttons, buttons, 5, order.id)

	def show_becomes_employee(self):
		self.GUI.tell('Вы стали сотрудником, поздравляем!')

	def show_limited(self):
		text = 'Вы слишком много раз отменили оцененные заказы, внесите предоплату за любой заказ либо подождите сутки'
		text = ' Оценка производится вручную, а дизайнер ценит свое время.'
		self.GUI.tell(text)
		time.sleep(5)

	def show_unprepaided_orders_limit_reached(self):
		self.GUI.tell('У вас 3 непредоплаченных заказа, больше нельзя =)')
		time.sleep(5)

	def show_wait_for_designer(self):
		self.GUI.tell_permanent(f'Заказ "{self.order.name}" передан дизайнеру для оценки, ожидайте.')
		if self.order.type in ['sketch','item']:
			text = 'После оценки будет известна примерная стоимость заказа.'
			text += ' Итоговая стоимость станет известна после моделирования.'
			self.GUI.tell(text)
		if self.order.type == 'item':
			text = 'После оценки вам нужно будет принести ваш предмет в пункт выдачи. Адрес и график работы находятся в разделе информации.'
			self.GUI.tell(text)
		time.sleep(3)

	def show_redirect_to_chat(self, order):
		text = f'Для продолжения общения по заказу "{order.name}" напишите в чат: @str3d_chat'
		self.GUI.tell_permanent(text)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		data = self.message.btn_data
		self.chat.context = ''
		if self.message.text == 'я_хочу_стать_сотрудником':
			self.chat.get_employed = True
			self.GUI.tell('Ждите подтверждения')
		elif data == 'order':
			self.show_order_menu()
		elif data == 'info':
			self.info.first_message(self.message)
		elif data == 'orders':
			self.show_orders()

	def process_order_menu(self):
		data = self.message.btn_data
		if self.cannot_make_orders(data):
			return
		if not data:
			self.show_top_menu()
			return
		self.order.type = data
		self.order.physical_status = 'prepare'
		# if data == 'farm model':
		# 	self.farm_model.first_message(self.message)
		if data in ['stl','link']:
			self.stl_link.first_message(self.message)
		elif data in ['sketch','item']:
			self.sketch_item.first_message(self.message)
		elif data == 'production':
			self.production.first_message(self.message)
		elif data == 'Назад':
			self.show_top_menu()
		else:
			return

	def process_orders(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		else:
			self.message.instance_id = int(self.message.btn_data)
			self.order_GUI.last_data = ''
			self.order_GUI.first_message(self.message)

	def process_order_payed(self):
		if self.message.btn_data == 'show':
			self.order_GUI.order = self.app.order_logic.get_order_by_id(self.message.instance_id)
			self.order_GUI.show_order()

	def process_sketch_screenshots(self):
		if self.message.btn_data == 'show':
			self.order_GUI.order = self.app.order_logic.get_order_by_id(self.message.instance_id)
			self.order_GUI.show_order()

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
				if order.logical_status == statuses or (statuses == [] or order.logical_status in statuses):
					orders.append(order)
		return orders

	def get_object_date(self, object):
		return object.created

	def penalty(self):
		self.orders_canceled += 1
		if self.orders_canceled >= 3:
			self.limit_date = date.today()
		self.app.db.update_chat(self.chat)

	def cannot_make_orders(self, data):
		if data in ['stl', 'link', 'sketch', 'item']:
			if self.is_limited():
				self.show_limited()
				return True
			elif self.is_unprepaided_orders_limit_reached():
				self.show_unprepaided_orders_limit_reached()
				return True
		return False

	def is_limited(self):
		if self.orders_canceled >= 3:  # repeated order cancelation limit
			period = (date.today() - self.limit_date).days
			if period >= 1:  # days to limit placing orders
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