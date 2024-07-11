import sys
import time
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Delivery:
	last_data = ''

	order = ''
	price = 0
	accepted_money = 0

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.message = None
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		self.GUI.clear_order_chat(message.instance_id)

		function = message.function
		if message.data_special_format:
			if self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				if function == '2':
					self.process_order_query()
				if function == '3':
					self.process_client()
				if function == '4':
					self.process_order_payed()
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
					self.process_item_received()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = f'Здравствуйте, {self.chat.user_name}. Выберите действие'
		buttons = []
		if self.app.order_logic.get_orders_by_status(self.app.orders, 'in_pick-up'):
			buttons.append('Выдать заказ')
		if self.app.order_logic.get_orders_by_status(self.app.orders, 'waiting_for_item'):
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
			text += 'Клиент может оплатить наличными либо переводом по инструкции на странице заказа.'
			buttons = [['Клиент оплатил наличными', 'cash']]
			buttons.append(['Клиент отказался от заказа', 'refused'])
			buttons.append(['Обновить данные', 'reload'])
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 3, self.order.id)

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
		text = f'Предоплата заказа не выполнена. Клиент может выполнить оплату переводом по инструкции на странице заказа либо наличными.'
		buttons = [['Клиент желает оплатить наличными', 'cash'], ['Обновить данные']]
		self.GUI.tell_buttons(text, buttons, buttons, 7, self.order.id)

	def show_item_prepay_amount(self):
		self.chat.set_context(self.address, 8)
		text = f'Минимальная сумма предоплаты: {self.order.get_remaining_prepayment()} рублей. Введите внесенную сумму:'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 8, self.order.id)

	def show_prepay_confirmation(self):
		text = f'Подтвердите внесение {self.accepted_money} рублей'
		buttons = [['Подтверждаю', 'confirm'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 9, self.order.id)

	def show_item_received(self):
		if self.order.is_payed():
			text = 'Оплата выполнена.'
		if self.order.is_prepayed():
			text = 'Преоплата выполнена.'
		text = f' Возьмите предмет клиента, наклейте на него этикетку с номером {self.order.delivery_code} и положите его в место приема.'
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
		try:
			code = int(self.message.text)
		except:
			self.GUI.tell('Неверный код')
			self.show_order_query()
			return
		order = self.app.order_logic.get_order_by_delivery_code(code)
		if not order:
			self.GUI.tell('Неверный код')
			self.show_order_query()
			return
		self.order = order
		order.delivery_user_id = self.chat.user_id
		self.show_client()

	def process_client(self):
		data = self.message.btn_data
		if data == 'issued':
			# self.order_issued(self.order)
			chat = self.app.get_chat(self.order.user_id)
			chat.user.GUI.tell(f'Заказ {self.order.name} выдан')
			self.order.logical_status = 'issued'
			self.order.remove()
			self.show_top_menu()
		elif data == 'cash':
			self.order.payment(self.order.remaining_payment())
			self.show_client()
		elif data == 'refused':
			self.order.logical_status = 'client_refused' # client doesn't get refund for prepayment
			self.show_top_menu()
		elif data == 'reload':
			self.last_data = ''
			self.show_client()
		elif data == 'Назад':
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
			time.sleep(1)
			self.show_top_menu()
			return
		order = self.app.order_logic.get_order_by_delivery_code(code)
		self.order = order
		if order:
			self.show_photos_confirm()
		else:
			self.GUI.tell('Код введен не верно')
			time.sleep(1)
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
			self.order.payment(self.accepted_money)
			self.app.db.update_order(self.order)
			self.update_pay_status()
		else:
			self.accepted_money = 0
			self.update_pay_status()

	def process_item_received(self):
		if self.message.btn_data == 'Задача выполнена':
			self.order.logical_status = 'item_received'
			self.app.db.update_order(self.order)
			self.show_top_menu()

#---------------------------- LOGIC ----------------------------

	def order_issued(self):
		self.order.logical_status = 'issued'
		time.sleep(5)
		self.show_top_menu()

	def update_pay_status(self):
		if self.order.is_prepayed():
			self.show_item_received()
		else:
			self.show_item_prepay()