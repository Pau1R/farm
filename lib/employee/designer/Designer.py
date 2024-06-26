import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.Texts import Texts
from lib.employee.designer.General import General
from lib.employee.designer.Production import Production
import ast

class Designer:
	address = ''

	app = None
	chat = None
	GUI = None
	texts = None
	message = None

	orders = []
	
	last_data = ''

	general = None
	production = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.orders = app.orders
		self.GUI = Gui(app, chat, address)
		self.texts = Texts(chat, address)

		self.general = General(app, chat, address + '/1')
		self.production = Production(app, chat, address + '/2')

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
				self.production.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				if function == '2':
					self.process_orders_design()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.last_data = ''
		text = '____________ 3D-дизайн ____________\n\n'
		
		logic = self.app.order_logic
		orders_of_type = logic.get_orders_by_type
		orders_of_status = logic.get_orders_by_status

		orders = orders_of_type(self.app.orders, ['stl','link','sketch','item'])
		orders = orders_of_status(orders, ['validate', 'prevalidate'])
		orders = logic.get_orders_by_user_id(orders, self.chat.user_id)
		amount = len(orders)
		if amount > 0:
			text += f'Задач в очереди: {amount}'
		else:
			text += 'Задачи отсутствуют'

		buttons = []
		validate = orders_of_status(self.orders, 'validate')
		validate = logic.get_orders_by_user_id(validate, self.chat.user_id)
			# buttons.append(['Настройка параметрических моделей','parametric'])
		if orders_of_type(validate, 'stl'):
			buttons.append(['Валидация файла модели', 'stl'])
		if orders_of_type(validate, 'link'):
			buttons.append(['Валидация ссылки', 'link'])

		# prevalidate
		prevalidate = orders_of_status(self.orders, 'prevalidate')
		preval = logic.get_orders_by_user_id(prevalidate, self.chat.user_id)
		if orders_of_type(prevalidate, 'sketch'):
			buttons.append(['Валидация чертежа', 'sketch,prevalidate'])
		if orders_of_type(prevalidate, 'item'):
			buttons.append(['Валидация фото', 'item,prevalidate'])
			
		if orders_of_type(validate, 'sketch'):
			buttons.append(['Разработка модели по чертежу', 'sketch'])
		if orders_of_type(validate, 'item'):
			buttons.append(['Разработка модели по образцу', 'item'])

		if orders_of_type(validate, 'production'):
			buttons.append(['Заявка на мелкосерийное производство', 'production'])

		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		data = self.message.btn_data.split(",")
		status = data[1] if len(data) > 1 else 'validate'
		data = data[0]
		if data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		elif data in ['stl','link','sketch','item']:
			self.general.last_data = ''
			self.general.first_message(self.message, data, status)
		elif data == 'production':
			self.production.last_data = ''
			self.production.first_message(self.message)
		# if data == 'parametric':
		# 	self.show_orders_parametric()