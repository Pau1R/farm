import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Order import Order
from lib.Texts import Texts

class Validate:
	address = '1/4/1'

	app = None
	chat = None
	GUI = None
	texts = None
	message = None
	last_data = ''

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
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
			elif message.function == '2':
				self.process_validate()
			elif message.function == '3':
				self.process_accept()
			elif message.function == '4':
				self.process_accept_quantity()
			elif message.function == '5':
				self.process_accept_weight()
			elif message.function == '6':
				self.process_accept_supports()
			elif message.function == '7':
				self.process_accept_supports_time()
			elif message.function == '8':
				self.process_accept_time()
			elif message.function == '9':
				self.process_accept_time_minutes()
			elif message.function == '10':
				self.process_accept_confirmation()
			elif message.function == '11':
				self.process_reject()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = self.texts.designer_orders_validate_text(self.order_timer, self.app.orders)
		buttons = self.texts.designer_orders_validate_btns(self.app.orders, self.app.chat)
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_validate(self):
		text = self.texts.designer_order_validate_text(self.order) # дизайнер слайсит модель и оценивает пригодность к печати. На 1 стол не более 900 грамм веса
		buttons = [['Принять модель', 'accept'], ['Отказать','reject'], ['Назад']] # 'Модель не рассчитана на 3д печать'
		self.GUI.tell_document_buttons(self.order.model_file, text, buttons, ['Назад'], 2, self.order.order_id)

	def show_accept(self):
		if not (self.order.conditions == '' or self.order.conditions == None):
			buttons = self.texts.spool_types
			buttons.append('любой')
			self.GUI.tell_buttons(f'Выберите тип материала. Условия эксплуатации: {self.order.conditions}', buttons, [], 3, self.order.order_id)
		else:
			self.show_accept_quantity()

	def show_accept_quantity(self):
		if self.order.quantity > 1:
			buttons = []
			for i in range(1, self.order.quantity + 1):
				buttons.append(i)
			self.GUI.tell_buttons('Выберите кол-во моделей на одном столе', buttons, [], 4, self.order.order_id)
		else:
			self.show_accept_weight()

	def show_accept_weight(self):
		self.app.chat.set_context(self.address, 5)
		self.GUI.tell('Введите вес стола в граммах')

	def show_accept_supports(self):
		self.GUI.tell_buttons('Нужно ли печатать поддержки?', ['Да','Нет'], [], 5, self.order.order_id)

	def show_accept_supports_time(self):
		text = 'Сколько нужно минут на удаление поддержек'
		if self.order.quantity > 1:
			text += ' с одной экземпляра'
		self.GUI.tell_buttons(text + '?', ['0.5','1','2','3','5','10','15','20'], [], 7, self.order.order_id)

	def show_accept_time(self):
		text = 'Продолжительность печати.\n\nВначале выберите сколько часов:'
		buttons = self.texts.order_validate_accept_time_btns
		self.GUI.tell_buttons(text, buttons, [], 8, self.order.order_id)

	def show_accept_time_minutes(self):
		text = 'Продолжительность печати.\n\nТеперь выберите сколько минут:'
		buttons = self.texts.order_validate_accept_time_minutes_btns
		self.GUI.tell_buttons(text, buttons, [], 9, self.order.order_id)

	def show_accept_confirmation(self):
		buttons = ['Подтвердить', 'Отмена']
		self.GUI.tell_buttons('Подтвердите валидацию', buttons, [], 10, self.order.order_id)

	def show_reject(self):
		self.set_context(11)
		self.app.chat.set_context(self.address, 11)
		self.GUI.tell('Напишите причину отказа')

	# def show_finished_orders(self):
	# 	buttons = []
	# 	buttons.extend(['Назад'])
	# 	self.GUI.tell_buttons('', buttons, ['Назад'], )

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.app.chat.user.designer.first_message(self.message)
		else:
			for order in self.app.orders:
				# if int(self.message.btn_data.split(":")[0]) == order.order_id:
				if int(self.message.btn_data) == order.order_id:
					self.order = order
					# self.show_validate()

					self.table_weight = 200
					self.table_quantity = 3
					self.table_hours = 4
					self.table_minutes = 10
					self.support_minutes = 1
					self.material = 'Любой'
					# self.material = 'PLA'
					self.process_accept_confirmation()

	def process_validate(self):
		if self.message.btn_data == 'Назад':
			self.order = None
			self.show_top_menu()
		elif self.message.btn_data == 'accept':
			self.show_accept()
		elif self.message.btn_data == 'reject':
			self.show_reject()

			# TODO:
			# - payment

	def process_accept(self):
		self.material = self.message.btn_data
		self.show_accept_quantity()

	def process_accept_quantity(self):
		try:
			self.table_quantity = int(self.message.btn_data)
			self.show_accept_weight()
		except:
			self.show_accept_quantity()

	def process_accept_weight(self):
		try:
			self.table_weight = int(self.message.text)
			self.show_accept_supports()
		except:
			self.show_accept_weight()

	def process_accept_supports(self):
		if self.message.btn_data == 'Да':
			self.supports = True
			self.show_accept_supports_time()
		else:
			self.supports = False
			self.show_accept_time()

	def process_accept_supports_time(self):
		try:
			self.support_minutes = int(self.message.btn_data)
		except:
			self.show_accept_supports_time()
		self.show_accept_time()

	def process_accept_time(self):
		try:
			self.table_hours = int(self.message.btn_data)
			self.show_accept_time_minutes()
		except:
			self.show_accept_time()

	def process_accept_time_minutes(self):
		try:
			self.table_minutes = int(self.message.btn_data)
			self.show_accept_confirmation()
		except:
			self.show_accept_time_minutes()

	def process_accept_confirmation(self):
		if self.message.btn_data == 'Отмена':
			self.show_validate()
		else:
			self.order.weight = self.table_weight / self.table_quantity
			self.order.time = (self.table_hours * 60) + self.table_minutes
			self.order.support_time = self.support_minutes
			self.order.status = 'validated'
			self.order.plastic_type = self.material
			# self.app.db.update_order(self.order)
			for chat in self.app.chats:
				if chat.user_id == str(self.order.user_id):
					chat.user.show_supports(self.order.order_id)
			self.show_top_menu()

	def process_reject(self):
		self.order.status = 'rejected'
		for chat in self.app.chats:
			if chat.user_id == str(self.order.user_id):
				chat.user.show_rejected(self.order.order_id, self.message.text)
		self.show_top_menu()