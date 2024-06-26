import sys
import time
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.Texts import Texts

class Delivery:
	address = ''

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''
	texts = None

	order = ''
	price = 0
	accepted_money = 0

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		self.GUI.clear_order_chat(message.instance_id)

		data = message.data
		function = message.function
		if message.data_special_format:
			if message.file3 == '' and (data == '' or data != self.last_data):
				self.last_data = data
				if function == '1':
					self.process_top_menu()
				if function == '2':
					self.process_order_query()
				if function == '3':
					self.process_issue_order()
				if function == '4':
					self.process_pay_for_order()
				if function == '5':
					self.process_item_id_query()
				if function == '6':
					self.process_photos_confirm()
				if function == '7':
					self.process_item_prepay()
				if function == '8':
					self.process_item_prepay_amount()
				if function == '9':
					self.process_prepay_confirmation()
				if function == '10':
					self.process_item_receive()
			# elif message.file3 == '1':
			# 	self.sub_something.new_message(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = f'Здравствуйте, {self.chat.user_name}. Выберите действие'
		buttons = []
		if self.app.order_logic.get_orders_by_status('in_pick-up', ''):
			buttons.append('Выдать заказ')
		if self.app.order_logic.get_orders_by_status('waiting_for_item', ''):
			buttons.append('Принять предмет')
		if not buttons:
			buttons.append('Обновить')
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_order_query(self):
		self.chat.set_context(self.address, 2)
		self.GUI.tell('Введите код получения заказа который сообщит вам клиент')

	def show_client(self):
		if self.order.is_payed():
			text = f'Выдайте заказ № {self.order.id}\n'
			buttons = [['Клиент забрал заказ', 'issued']]
		else:
			text = f'Предоставьте заказ № {self.order.id} клиенту для ознакомления.\n'
			text += f'Заказ оплачен не полностью. Сумма доплаты: {self.order.remaining_payment()} рублей\n\n'
			text += 'Клиент может оплатить наличными либо переводом через чат-бот на странице заказа.'
			buttons = [['Клиент оплатил наличными', 'payed']]
			buttons.append(['Клиент отказался от заказа', 'refused'])
		self.GUI.tell_buttons(text, buttons, buttons, 3, self.order.id)

	def show_order_payed(self, order):
		text = f'Заказ № {self.order.id} оплачен полностью'
		buttons = [['Клиент забрал заказ', 'issued']]
		message = self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.id)
		message.general_clear = False

	def show_item_id_query(self):
		self.chat.set_context(self.address, 5)
		self.GUI.tell('Попросите клиента назвать вам код передачи и введите его.')

	def show_photos_confirm(self):
		for photo in self.order.sketches:
			self.GUI.tell_photo('', photo[0])
		text = f'Подтвердите соответствие фотографий предмету клиента. Если нет соответствия, предмет принимать нельзя.'
		buttons = [['Подтверждаю', 'confirm'], 'Не соответствуют']
		self.GUI.tell_buttons(text, buttons, buttons, 6, self.order.id)

	def show_item_prepay(self):
		text = f'Предоплата заказа не выполнена. Клиент может выполнить оплату переводом через чат-бот либо наличными.'
		buttons = [['Клиент желает оплатить наличными', 'cash'], ['Обновить данные']]
		self.GUI.tell_buttons(text, buttons, buttons, 7, self.order.id)

	def show_item_prepay_amount(self):
		self.chat.set_context(self.address, 8)
		text = f'Минимальная сумма предоплаты: {self.order.get_prepayment_price()} рублей. Введите внесенную сумму:'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 8, self.order.id)

	def show_prepay_confirmation(self):
		text = f'Подтвердите внесение {self.accepted_money} рублей'
		buttons = [['Подтверждаю', 'confirm'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 9, self.order.id)

	def show_item_receive(self):
		text = f'Оплата выполнена. Возьмите предмет клиента, наклейте на него этикетку с номером {self.order.delivery_code} и положите его в место приема.'
		buttons = ['Задача выполнена']
		self.GUI.tell_buttons(text, buttons, buttons, 10, self.order.id)

#---------------------------- PROCESS ----------------------------
	
	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)
		elif data == 'Выдать заказ':
			self.show_order_query()
		elif data == 'Принять предмет':
			self.show_item_id_query()
		elif data == 'Обновить':
			self.last_data = ''
			self.show_top_menu()

	def process_order_query(self):
		code = self.message.text
		order = self.app.order_logic.get_order_by_delivery_code(code)
		self.order = order
		order.delivery_user_id = self.chat.user_id
		self.show_client()

	def process_client(self):
		data = self.message.btn_data
		if data == 'issued' or data == 'payed':
			self.order_issued(self.order)
		elif data == 'refused':
			self.order.logical_status = 'client_refused' # client doesn't get refund for prepayment
			self.show_top_menu()

	def process_order_payed(self):
		if self.message.btn_data == 'issued':
			order = self.app.order_logic.get_order_by_id(self.message.instance_id)
			self.order_issued(order)

	def process_item_id_query(self):
		try:
			code = int(self.message.text)
		except:
			self.GUI.tell('Код введен не верно')
			time.sleep(3)
			self.show_top_menu()
			return
		order = self.app.order_logic.get_order_by_delivery_code(code)
		self.order = order
		if order:
			self.show_photos_confirm()
		else:
			self.GUI.tell('Код введен не верно')
			time.sleep(3)
			self.show_top_menu()

	def process_photos_confirm(self):
		data = self.message.btn_data
		if data == 'confirm':
			self.update_pay_status()
		else:
			self.show_top_menu()

	def process_item_prepay(self):
		data = self.message.btn_data
		if data == 'cash':
			self.show_item_prepay_amount()
		elif data == 'Обновить данные':
			self.last_data = ''
			self.update_pay_status()

	def process_item_prepay_amount(self):
		try:
			self.accepted_money = int(self.message.text)
			self.show_prepay_confirmation()
		except:
			tell('Ошибка ввода данных')
			self.update_pay_status()

	def process_prepay_confirmation(self):
		data = self.message.btn_data
		if data == 'confirm':
			self.order.order_payed(self.accepted_money)
			self.app.db.update_order(self.order)
			self.update_pay_status()
		else:
			self.accepted_money = 0
			self.update_pay_status()

	def process_item_receive(self):
		if self.message.btn_data == 'Задача выполнена':
			self.order.logical_status = 'item_received' # TODO: think of status. Save to db
			self.show_top_menu()

#---------------------------- LOGIC ----------------------------

	def order_issued(self, order):
		self.order.logical_status = 'issued'
		time.sleep(5)
		self.show_top_menu()

	def update_pay_status(self):
		if self.order.is_prepayed():
			self.show_item_receive()
		else:
			self.show_item_prepay()