import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.clients.Order import Order
from lib.Texts import Texts

class Validate:
	app = None
	chat = None
	GUI = None
	texts = None
	message = None
	context = ''

	order = None
	orders = []
	order_timer = ''

	table_quantity = 1
	table_weight = 1
	table_hours = 1
	table_minutes = 1
	supports = False
	support_minutes = 0
	material = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat)
		self.texts = Texts()

	def first_message(self, message):
		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.messages.append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_top_menu()
		elif context == 'top_menu':
			self.process_top_menu()
		elif context == 'validate':
			self.process_validate()
		elif context == 'accept':
			self.process_accept()
		elif context == 'accept_quantity':
			self.process_accept_quantity()
		elif context == 'accept_weight':
			self.process_accept_weight()
		elif context == 'accept_supports':
			self.process_accept_supports()
		elif context == 'accept_supports_time':
			self.process_accept_supports_time()
		elif context == 'accept_time':
			self.process_accept_time()
		elif context == 'accept_time_minutes':
			self.process_accept_time_minutes()
		elif context == 'accept_confirmation':
			self.process_accept_confirmation()
		elif context == 'reject':
			self.process_reject()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		buttons = self.texts.designer_orders_validate_btns(self.app.orders, self.app.chat)
		self.GUI.tell_buttons(self.texts.designer_orders_validate_text(self.order_timer, self.app.orders), buttons, buttons)

	def show_validate(self):
		self.context = 'validate' # дизайнер слайсит модель и оценивает пригодность к печати. На 1 стол не более 900 грамм веса
		buttons = [['Принять модель', 'accept'], ['Отказать','reject'], ['Назад']] # 'Модель не рассчитана на 3д печать'
		self.GUI.tell_document_buttons(self.order.model_file, self.texts.designer_order_validate_text(self.order), buttons, ['Назад'])

	def show_accept(self):
		self.context = 'accept'
		if not (self.order.conditions == '' or self.order.conditions == None):
			buttons = self.texts.spool_types
			buttons.append('любой')
			self.GUI.tell_buttons(f'Выберите тип материала. Условия эксплуатации: {self.order.conditions}', buttons, [])
		else:
			self.show_accept_quantity()

	def show_accept_quantity(self):
		self.context = 'accept_quantity'
		if self.order.quantity > 1:
			buttons = []
			for i in range(1, self.order.quantity + 1):
				buttons.append(i)
			self.GUI.tell_buttons('Выберите кол-во моделей на одном столе', buttons, [])
		else:
			self.show_accept_weight()

	def show_accept_weight(self):
		self.context = 'accept_weight'
		self.GUI.tell('Введите вес стола в граммах')

	def show_accept_supports(self):
		self.context = 'accept_supports'
		self.GUI.tell_buttons('Нужно ли печатать поддержки?', ['Да','Нет'], [])

	def show_accept_supports_time(self):
		self.context = 'accept_supports_time'
		text = 'Сколько нужно минут на удаление поддержек'
		if self.order.quantity > 1:
			text += ' с одной экземпляра'
		self.GUI.tell_buttons(text + '?', ['0.5','1','2','3','5','10','15','20'], [])

	def show_accept_time(self):
		self.context = 'accept_time'
		self.GUI.tell_buttons('Продолжительность печати.\n\nВначале выберите сколько часов:', self.texts.order_validate_accept_time_btns, [])

	def show_accept_time_minutes(self):
		self.context = 'accept_time_minutes'
		self.GUI.tell_buttons('Продолжительность печати.\n\nТеперь выберите сколько минут:', self.texts.order_validate_accept_time_minutes_btns, [])

	def show_accept_confirmation(self):
		self.context = 'accept_confirmation'
		buttons = ['Подтвердить', 'Отмена']
		self.GUI.tell_buttons('Подтвердите валидацию', buttons, [])

	def show_reject(self):
		self.context = 'reject'
		self.GUI.tell('Напишите причину отказа')

	def show_finished_orders(self):
		self.context = 'finished_orders'
		buttons = []
		buttons.extend(['Назад'])
		self.GUI.tell_buttons('', buttons, ['Назад'])

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Назад':
			self.app.chat.user.employee.menu = None
			self.app.chat.user.employee.first_message(self.message)
		else:
			for order in self.app.orders:
				if int(self.message.data.split(":")[0]) == order.order_id:
					self.order = order
					# self.show_validate()

					self.table_weight = 200
					self.table_quantity = 3
					self.table_hours = 4
					self.table_minutes = 10
					self.support_minutes = 1
					# self.material = 'Любой'
					self.material = 'PETG'
					self.process_accept_confirmation()

	def process_validate(self):
		self.context = ''
		if self.message.data == 'Назад':
			self.order = None
			self.show_top_menu()
		elif self.message.data == 'accept':
			self.show_accept()
		elif self.message.data == 'reject':
			self.show_reject()

			# TODO:
			# - payment

	def process_accept(self):
		self.context = ''
		self.material = self.message.data
		self.show_accept_quantity()

	def process_accept_quantity(self):
		self.context = ''
		try:
			self.table_quantity = int(self.message.data)
			self.show_accept_weight()
		except:
			self.show_accept_quantity()

	def process_accept_weight(self):
		self.context = ''
		try:
			self.table_weight = int(self.message.text)
			self.show_accept_supports()
		except:
			self.show_accept_weight()

	def process_accept_supports(self):
		self.context = ''
		if self.message.data == 'Да':
			self.supports = True
			self.show_accept_supports_time()
		else:
			self.supports = False
			self.show_accept_time()

	def process_accept_supports_time(self):
		self.context = ''
		try:
			self.support_minutes = int(self.message.data)
		except:
			self.show_accept_supports_time()
		self.show_accept_time()

	def process_accept_time(self):
		self.context = ''
		try:
			self.table_hours = int(self.message.data)
			self.show_accept_time_minutes()
		except:
			self.show_accept_time()

	def process_accept_time_minutes(self):
		self.context = ''
		try:
			self.table_minutes = int(self.message.data)
			self.show_accept_confirmation()
		except:
			self.show_accept_time_minutes()

	def process_accept_confirmation(self):
		self.context = ''
		if self.message.data == 'Отмена':
			self.show_validate()
		else:
			self.order.weight = self.table_weight / self.table_quantity
			self.order.time = (self.table_hours * 60) + self.table_minutes
			self.order.support_time = self.support_minutes
			self.order.status = 'validated'
			self.order.plastic_type = self.material
			for chat in self.app.chats:
				if chat.user_id == str(self.order.user_id):
					chat.user.show_supports(self.order.order_id)
			self.show_top_menu()

	def process_reject(self):
		self.context = ''
		self.order.status = 'rejected'
		for chat in self.app.chats:
			if chat.user_id == str(self.order.user_id):
				chat.user.show_rejected(self.order.order_id, self.message.text)
		self.show_top_menu()