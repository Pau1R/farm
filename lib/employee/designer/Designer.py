import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.Texts import Texts
from lib.employee.designer.Stl import Stl
from lib.employee.designer.Link import Link
from lib.employee.designer.Sketch import Sketch
from lib.employee.designer.Item import Item
from lib.employee.designer.Production import Production

class Designer:
	address = ''

	app = None
	chat = None
	GUI = None
	texts = None
	message = None

	orders = []
	
	last_data = ''

	stl = None
	link = None
	sketch = None
	item = None
	production = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.orders = app.orders
		self.GUI = Gui(app, chat, address)
		self.texts = Texts(chat, address)

		self.stl = Stl(app, chat, address + '/1')
		self.link = Link(app, chat, address + '/2')
		self.sketch = Sketch(app, chat, address + '/3')
		self.item = Item(app, chat, address + '/4')
		self.production = Production(app, chat, address + '/5')

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
				self.stl.new_message(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.last_data = ''
		text = f'Здравствуйте, дизайнер {self.chat.user_name}. '
		amount = 0
		for order in self.orders:
			if order.logical_status == 'validate':
				amount += 1
		if amount > 0:
			text += f'Задач в очереди: {amount}'
		else:
			text += 'Задачи отсутствуют'

		buttons = []
		all_orders = self.app.order_logic.get_orders_by_status('', 'validate')
			# buttons.append(['Настройка параметрических моделей','parametric'])
		if self.app.order_logic.get_orders_by_type(all_orders, 'stl'):
			buttons.append(['Валидация файла модели', 'stl'])
		if self.app.order_logic.get_orders_by_type(all_orders, 'link'):
			buttons.append(['Валидация модели из интернета', 'link'])
		if self.app.order_logic.get_orders_by_type(all_orders, 'design'):
			buttons.append(['Разработка модели по чертежу', 'design'])
		if self.app.order_logic.get_orders_by_type(all_orders, 'item'):
			buttons.append(['Оценка пригодности предмета к копированию', 'item'])
		if self.app.order_logic.get_orders_by_type(all_orders, 'production'):
			buttons.append(['Заявка на мелкосерийное производство', 'production'])

		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	# def show_orders_design(self):
	# 	self.last_data = ''
	# 	text = self.texts.designer_orders_design_text(self.order_timer, self.app.orders)
	# 	buttons = self.texts.designer_orders_design_btns(self.order)
	# 	self.GUI.tell_buttons(text, buttons, ['Назад'], 2, 0)

	# def show_order(self):
	# 	self.last_data = ''
	# 	text = self.texts.designer_order_text(self.order)
	# 	buttons = self.texts.designer_order_btns(self.order_timer, self.order)
	# 	self.GUI.tell_buttons(text, buttons, ['Назад'], 3, self.order.id)
		
	# def show_finished_orders(self):
	# 	self.last_data = ''
	# 	buttons = []
	# 	buttons.extend(['Назад'])
	# 	self.GUI.tell_buttons('', buttons, ['Назад'], 4, 0)

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		elif data == 'stl':
			self.stl.last_data = ''
			self.stl.first_message(self.message)
		elif data == 'link':
			self.link.last_data = ''
			self.link.first_message(self.message)
		elif data == 'sketch':
			self.sketch.last_data = ''
			self.sketch.first_message(self.message)
		elif data == 'item':
			self.item.last_data = ''
			self.item.first_message(self.message)
		elif data == 'production':
			self.production.last_data = ''
			self.production.first_message(self.message)
		# if data == 'parametric':
		# 	self.show_orders_parametric()
		# if data == 'finished':
		# 	self.show_finished_orders()