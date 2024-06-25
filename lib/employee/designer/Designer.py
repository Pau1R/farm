import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.Texts import Texts
from lib.employee.designer.Process import Process
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

	validate = None
	production = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.orders = app.orders
		self.GUI = Gui(app, chat, address)
		self.texts = Texts(chat, address)

		self.validate = Process(app, chat, address + '/1')
		self.production = Production(app, chat, address + '/2')

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
					self.process_orders_design()
			elif message.file3 == '1':
				self.validate.new_message(message)
			elif message.file3 == '2':
				self.production.new_message(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.last_data = ''
		text = '____________ 3D-дизайн ____________\n\n'
		logic = self.app.order_logic
		orders = logic.get_orders_by_type(self.app.orders, ['stl','link','sketch','item'])
		orders = logic.get_orders_by_status(orders, ['validate', 'prevalidate'])
		orders = logic.get_orders_by_user_id(orders, self.chat.user_id)
		amount = len(orders)
		if amount > 0:
			text += f'Задач в очереди: {amount}'
		else:
			text += 'Задачи отсутствуют'

		buttons = []
		orders_validate = logic.get_orders_by_status(self.orders, 'validate')
		orders_validate = logic.get_orders_by_user_id(orders_validate, self.chat.user_id)
		orders_prevalidate = logic.get_orders_by_status(self.orders, 'prevalidate')
		orders_prevalidate = logic.get_orders_by_user_id(orders_prevalidate, self.chat.user_id)
			# buttons.append(['Настройка параметрических моделей','parametric'])
		if logic.get_orders_by_type(orders_validate, 'stl'):
			buttons.append(['Валидация файла модели', ['stl', 'validate']])
		if logic.get_orders_by_type(orders_validate, 'link'):
			buttons.append(['Валидация ссылки', ['link', 'validate']])

		if logic.get_orders_by_type(orders_prevalidate, 'sketch'):
			buttons.append(['Валидация чертежа', ['sketch', 'prevalidate']])
		if logic.get_orders_by_type(orders_prevalidate, 'item'):
			buttons.append(['Валидация фото', ['item', 'prevalidate']])
			
		if logic.get_orders_by_type(orders_validate, 'sketch'):
			buttons.append(['Разработка модели по чертежу', ['sketch', 'validate']])
		if logic.get_orders_by_type(orders_validate, 'item'):
			buttons.append(['Разработка модели по образцу', ['item', 'validate']])

		if logic.get_orders_by_type(orders_validate, 'production'):
			buttons.append(['Заявка на мелкосерийное производство', 'production'])

		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		else:
			data = ast.literal_eval(data)
			status = data[1]
			data = data[0]
		if data in ['stl','link','sketch','item']:
			self.validate.last_data = ''
			self.validate.first_message(self.message, data, status)
		elif data == 'production':
			self.production.last_data = ''
			self.production.first_message(self.message)
		# if data == 'parametric':
		# 	self.show_orders_parametric()