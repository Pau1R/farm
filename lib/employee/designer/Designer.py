import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.Texts import Texts
from lib.employee.designer.Validate import Validate

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

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.orders = app.orders
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, '1/4')
		self.validate = Validate(app, chat)

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

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.last_data = ''
		text = f'Здравствуйте, дизайнер {self.chat.user_name}. '
		amount = 0
		for order in self.orders:
			if order.status == 'validate':
				amount += 1
		if amount > 0:
			text += f'Задач в очереди: {amount}'
		else:
			text += 'Задачи отсутствуют'
		buttons = [['Разработка моделей по чертежу', 'design']] 
		buttons.append(['Валидация моделей', 'validate'])
		buttons.append(['Настройка параметрических моделей','parametric'])
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'], 1, 0)

	def show_orders_design(self):
		self.last_data = ''
		text = self.texts.designer_orders_design_text(self.order_timer, self.app.orders)
		buttons = self.texts.designer_orders_design_btns(self.order)
		self.GUI.tell_buttons(text, buttons, ['Назад'], 2, 0)

	def show_order(self):
		self.last_data = ''
		text = self.texts.designer_order_text(self.order)
		buttons = self.texts.designer_order_btns(self.order_timer, self.order)
		self.GUI.tell_buttons(text, buttons, ['Назад'], 3, self.order.id)
		
	def show_finished_orders(self):
		self.last_data = ''
		buttons = []
		buttons.extend(['Назад'])
		self.GUI.tell_buttons('', buttons, ['Назад'], 4, 0)

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		if self.message.btn_data == 'design':
			self.show_orders_design()
		if self.message.btn_data == 'validate':
			self.validate.last_data = ''
			self.validate.first_message(self.message)
		if self.message.btn_data == 'parametric':
			self.show_orders_parametric()
		if self.message.btn_data == 'finished':
			self.show_finished_orders()

	def process_orders_design(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		for order in self.app.orders:
			if order.id == self.message.instance_id:
				self.order = order
				self.show_order()

	def process_finished_orders(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()