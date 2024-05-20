import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts

class Client_order:
	address = '1/4'
	
	app = None
	chat = None
	message = None
	order = None
	GUI = None
	context = ''
	texts = None
	color = None
	last_data = ''

	order = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(app)

	def first_message(self, message):
		self.message = message
		self.set_order()
		self.show_order()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		self.set_order()
		self.GUI.clear_order_chat(self.order.order_id)

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_order()
			elif message.function == '2':
				self.process_supports()
			elif message.function == '3':
				self.process_cancel_confirmation()
			elif message.function == '4':
				self.process_confirmed_by_designer()
		if message.type == 'text':
			self.GUI.messages_append(message)

	def set_order(self):
		order_id = int(self.message.instance_id)
		for order in self.app.orders:
			if order.order_id == order_id:
				self.order = order
				return

#---------------------------- SHOW ----------------------------

	def show_order(self):
		order = self.order
		settings_set = False
		free_start = False
		prepayed = True
		status = ''

		# set parameters
		prepay_price = order.prepayment_percent * order.price + 5
		if order.plastic_color != '' and order.support_remover != '':
			settings_set = True
		if order.price < self.app.settings.prepayment_free_max and order.price < (self.chat.user.money_payed / 2):
			free_start = True
		elif order.prepayed < prepay_price:
			prepayed = False

		if order.status == 'validate':
			status = 'Ожидание дизайнера'
		elif order.status == 'validated':
			status = 'Ожидание действий клиента'
		elif order.status == 'prepayed':
			status = 'Выполняется'

		# set text
		text = order.name + '\n\n'
		text += f'Статус: {status.lower()}\n'
		if order.price > 0:
			if settings_set:
				text += 'С'
			else:
				text += 'Предварительная с'
			text += f'тоимость: {order.price} рублей\n'
		if order.quantity > 1:
			text += f'Кол-во экземпляров: {order.quantity}\n'
		if order.weight > 0:
			if order.quantity > 1:
				text0 = 'Общий вес'
			else:
				text0 = 'Вес'
			text += f'{text0}: {int(order.weight) * order.quantity} грамм\n'
		if order.plastic_type != '':
			text += f'Тип материала: {order.plastic_type.lower()}\n'
		if order.plastic_color != '':
			text += f'Цвет изделия: {order.plastic_color.lower()}\n'
		if order.time > 0:
			text += f'Длительность печати'
			if order.time > 119: # if 2 hours or more show only hours amount
				text += f' (часов): {int(order.time/60)}\n'
			else:
				text += f': {int(order.time)} минут\n'
		if order.start_time_estimate != None:
			text += f'Дата готовности (примерно):' # TODO: {order.start_time_estimate}\n'
		if order.support_remover != '':
			text += f'Удаление поддержек: {order.support_remover.lower()}\n'
		if order.prepayed > 0:
			if not free_start and not prepayed:
				text += f'Предоплачено: {int(order.prepayed)}/{int(prepay_price)} рублей'
			else:
				text += f'Предоплачено: {int(order.prepayed)} рублей'

		# set buttons
		buttons = []
		# order.plastic_color = ''
		# status = 'validated'
		if order.status == 'validated':
			if order.plastic_color == '':
				buttons.append(['Выбрать цвет', 'color'])
			elif order.support_remover == '':
				buttons.append(['Выбрать кто уберет поддержки', 'supports'])
			elif settings_set:
				# Условия принятия заказа без предоплаты:
				# 1) Стоимость заказа меньше лимита
				# 2) Стоимость заказа меньше половины стоимости выполненных заказов
				if free_start:
					buttons.append(['Подтвердить и передать на выполнение', 'continue'])
				else:
					buttons.append(['Внести предоплату', 'prepay'])

		buttons.append(['Отменить заказ'])
		buttons.append(['Назад'])
		self.GUI.tell_buttons(text, buttons, buttons, 1, order.order_id)

	def show_supports(self):
		text = 'Вы хотите убрать поддержки самостоятельно? Цена заказа будет меньше на '
		text += f'{int(self.order.support_time * self.order.quantity * self.app.settings.support_remove_price)} рублей'
		buttons = [['Да, уберу сам', 'Клиент'], ['Нет, уберите вы', 'Магазин'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, self.order.order_id)

	def show_cancel_confirmation(self):
		text = 'Подтвердите удаление заказа'
		buttons = [['Да, подтверждаю', 'confirm'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 3, self.order.order_id)

	def show_confirmed_by_designer(self, order):
		text = f'Оценка заказа {order.name} выполнена'
		buttons = [['Перейти к заказу', 'now'], ['Перейти к заказу попозже', 'then']]
		message = self.GUI.tell_buttons(text, buttons, buttons, 4, order.order_id)
		message.general_clear = False

#---------------------------- PROCESS ----------------------------

	def process_order(self):
		data = self.message.btn_data
		if data == 'color':
			self.chat.user.client_color.last_data = ''
			self.chat.user.client_color.first_message(self.message)
		elif data == 'supports':
			self.show_supports()
		elif data == 'continue':
			x = ''
		elif data == 'prepay':
			x = ''
		elif data == 'Отменить заказ':
			self.show_cancel_confirmation()
		elif data == 'Назад':
			self.chat.user.last_data = ''
			self.chat.user.show_orders()

	def process_supports(self):
		data = self.message.btn_data
		if data == 'Клиент':
			self.order.support_remover = 'Клиент'
			self.order.price -= int(self.order.support_time * self.order.quantity * self.app.settings.support_remove_price)
		elif data == 'Магазин':
			self.order.support_remover = 'Магазин'
		self.app.db.update_order(self.order)
		self.show_order()

	def process_cancel_confirmation(self):
		if self.message.btn_data == 'confirm':
			self.app.orders.remove(self.order)
			self.app.db.remove_order(self.order)
			self.order = None
			self.chat.user.last_data = ''
			self.chat.user.show_orders()
			return
		self.show_order()

	def process_confirmed_by_designer(self):
		if self.message.btn_data == 'now':
			self.show_order()

#---------------------------- LOGIC ----------------------------