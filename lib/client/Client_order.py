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
				self.process_color()
		if message.type == 'text':
			self.GUI.messages_append(message)

	def set_order(self):
		order_id = self.message.instance_id
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

		# set parameters
		prepay_price = order.prepayment_percent * order.price
		if order.plastic_color != '' and order.support_remover != '':
			settings_set = True
		if order.price < self.app.prepayment_free_max and order.price < (self.chat.user.money_payed / 2):
			free_start = True
		elif order.prepayed < prepay_price:
			prepayed = False

		# set text
		text = order.name + '\n\n'
		text += f'Статус: {status}\n'
		if settings_set:
			text += 'С'
		else:
			text += 'Предварительная с'
		text += f'тоимость: {order.price} rub\n'
		if order.quantity > 1:
			text += f'Кол-во экземпляров: {order.quantity}\n'
		if order.quantity > 1:
			text0 = 'Общий вес'
		else:
			text0 = 'Вес'
		text += f'{text0}: {int(order.weight) * order.quantity} грамм\n'
		text += f'Длительность печати'
		if order.time > 119: # if 2 hours or more show only hours amount
			text += f' (часов): {int(order.time/60)}'
		else:
			text += f': {int(order.time)} минут'
		if order.start_time_estimate != None:
			text += f'\nДата готовности (примерно):' # TODO: {order.start_time_estimate}'
		if order.support_remover != '':
			text += f'\nУдаление поддержек: {order.support_remover}'
		if order.prepayed > 0:
			if not free_start and not prepayed:
				text += f'Предоплачено: {order.prepayed}/{prepay_price} rub'
			else:
				text += f'Предоплачено: {order.prepayed} rub'

		# set buttons
		buttons = []
		if order.status == 'validate':
			status = 'Ожидание дизайнера'
		elif order.status == 'validated':
			status = 'Оформление'
			if order.plastic_color == '':
				buttons.append(['Выбрать цвет', 'color'])
			elif order.support_remover == '':
				buttons.append(['Удаление поддержек', 'supports'])
			elif settings_set:
				# Условия принятия заказа без предоплаты:
				# 1) Стоимость заказа меньше лимита
				# 2) Стоимость заказа меньше половины стоимости выполненных заказов
				if free_start:
					buttons.append(['Подтвердить и передать на выполнение', 'continue'])
				else:
					buttons.append(['Внести предоплату', 'prepay'])
		elif order.status == 'prepayed':
			status = 'Выполняется'

		buttons.append(['Отменить заказ'])
		buttons.append(['Назад'])
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

#---------------------------- PROCESS ----------------------------



#---------------------------- LOGIC ----------------------------