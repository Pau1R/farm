import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.order.GUI import Order_GUI
from lib.employee.designer.General import General
import ast

class Designer:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.message = None
		self.address = address
		self.orders = app.orders
		self.GUI = Gui(app, chat, address)

		self.general = General(app, chat, address + '/1')
		self.order_GUI = Order_GUI(app, chat, address + '/2')

		self.screenshots = []

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				self.general.new_message(message)
			if file == '2':
				self.order_GUI.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				if function == '2':
					self.process_new_order()
				if function == '3':
					self.process_sketch_prepayed()
				if function == '4':
					self.process_screenshots()
				if function == '5':
					self.process_design_confirmed()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.last_data = ''
		text = '____________ 3D-дизайн ____________\n\n'
		
		logic = self.app.order_logic
		orders_of_type = logic.get_orders_by_type
		orders_of_status = logic.get_orders_by_status

		orders = orders_of_type(self.app.orders, ['stl','link','sketch','item','production'])
		orders = orders_of_status(orders, ['validate', 'prevalidate', 'waiting_for_design', 'clarify'])
		orders = logic.get_orders_by_user_id(orders, self.chat.user_id)
		amount = len(orders)
		if amount > 0:
			text += f'Задач в очереди: {amount}'
		else:
			text += 'Задачи отсутствуют'

		buttons = []

		# validate
		validate = orders_of_status(self.orders, 'validate')
		validate = logic.get_orders_by_user_id(validate, self.chat.user_id)
			# buttons.append(['Настройка параметрических моделей','parametric'])
		if orders_of_type(validate, 'stl'):
			buttons.append(['Валидация файла модели', 'stl'])
		if orders_of_type(validate, 'link'):
			buttons.append(['Валидация ссылки', 'link'])

		# prevalidate
		prevalidate = orders_of_status(self.orders, 'prevalidate')
		prevalidate = logic.get_orders_by_user_id(prevalidate, self.chat.user_id)
		if orders_of_type(prevalidate, 'sketch'):
			buttons.append(['Валидация чертежа', 'sketch,prevalidate'])
		if orders_of_type(prevalidate, 'item'):
			buttons.append(['Валидация фото', 'item,prevalidate'])
		
		# design
		waiting_for_design = orders_of_status(self.orders, 'waiting_for_design')
		waiting_for_design = logic.get_orders_by_user_id(waiting_for_design, self.chat.user_id)
		if orders_of_type(waiting_for_design, 'sketch'):
			buttons.append(['Разработка модели по чертежу', 'sketch,waiting_for_design'])
		# TODO: show button for 'clarify' orders
		if orders_of_type(waiting_for_design, 'item'):
			buttons.append(['Разработка модели по образцу', 'item,waiting_for_design'])

		# production
		if orders_of_type(validate, 'production'):
			buttons.append(['Заявка на мелкосерийное производство', 'production'])

		buttons.append(['Обновить','update'])
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_new_order(self, order):
		text = 'Новая задача - валидация '
		if order.type == 'stl':
			text += 'файла'
		elif order.type == 'link':
			text += 'ссылки'
		elif order.type == 'sketch':
			text += 'чертежа'
		elif order.type == 'item':
			text += 'предмета по фотографиям'
		elif order.type == 'production':
			text += 'мелкосерийного заказа'
		text += f': {order.name} (№ {order.id})'
		buttons = [['Перейти к заказу','show']]
		self.GUI.tell_buttons(text, buttons, buttons, 2, order.id)

	def show_sketch_prepayed(self, order):
		text = f'Новая задача - разработка модели: "{order.name}" (№ {order.id})'
		buttons = [['Перейти к заказу','show']]
		self.GUI.tell_buttons(text, buttons, buttons, 3, order.id)

	def show_screenshots(self, order):
		self.chat.set_context(self.address, 4)
		self.order = order
		text = 'Загрузите несколько скриншотов разработанной модели'
		buttons = []
		if self.screenshots:
			text += f'\n\nскриншотов загружено: {len(self.screenshots)}'
			buttons.append(['Загрузку закончил', 'uploaded'])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 4, order.id)

	def show_design_confirmed(self, order):
		text = f'Клиент подтвердил модель заказа "{order.name}" (№ {order.id})'
		buttons = [['Перейти к заказу','show']]
		self.GUI.tell_buttons(text, buttons, buttons, 5, order.id)

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		data = self.message.btn_data.split(",")
		status = data[1] if len(data) > 1 else 'validate'
		data = data[0]
		if data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		elif data == 'update':
			self.show_top_menu()
		elif data in ['stl','link','sketch','item','production']:
			self.general.last_data = ''
			self.general.first_message(self.message, data, status)
		# if data == 'parametric':
		# 	self.show_orders_parametric()

	def process_new_order(self):
		if self.message.btn_data == 'show':
			self.show_order()

	def process_sketch_prepayed(self):
		if self.message.btn_data == 'show':
			self.show_order()

	def process_screenshots(self):
		order = self.order
		data = self.message.btn_data
		if data == 'Назад':
			self.screenshots = []
			self.order_GUI.show_order()
		elif data == 'uploaded':
			order.logical_status = 'client_check'
			order.screenshots = self.screenshots
			self.app.db.update_order(order)
			chat = self.app.get_chat(order.user_id)
			chat.user.show_sketch_screenshots(order)
			self.general.show_top_menu()
		else:
			file_id = self.message.file_id
			if file_id and self.message.type in ['photo']:
				self.screenshots.append(file_id)
			self.show_screenshots(order)

	def process_design_confirmed(self):
		if self.message.btn_data == 'show':
			self.show_order()

#---------------------------- LOGIC ----------------------------

	def show_order(self):
		self.order_GUI.last_data = ''
		self.order_GUI.first_message(self.message)