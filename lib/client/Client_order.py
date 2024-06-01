import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts
import time
import random

class Client_order:
	address = '1/4'
	
	app = None
	chat = None
	message = None
	order = None
	order_waiting = None
	GUI = None
	context = ''
	texts = None
	color = None
	last_data = ''

	order = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
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
				self.process_pay()
			elif message.function == '4':
				self.process_cancel_confirmation()
			elif message.function == '5':
				self.process_confirmed_by_designer()
			elif message.function == '6':
				self.process_reject_reason()
		if message.type == 'text':
			self.GUI.messages_append(message)

	def set_order(self):
		try:
			order_id = int(self.message.instance_id)
			for order in self.app.orders:
				if order.order_id == order_id:
					self.order = order
					return
		except:
			if self.order_waiting != None:
				self.order = self.order_waiting
				self.order_waiting = None

#---------------------------- SHOW ----------------------------

	def show_order(self):
		order = self.order

		# set parameters
		settings_set = False
		if order.color_id != 0 and (order.support_remover != '' or order.support_time == 0):
			if order.prepayment_percent == 0:
				order.prepayment_percent = int(self.app.settings.get('prepayment_percent'))
				self.app.db.update_order(self.order)
			settings_set = True
		free_start = order.is_free_start()
		prepayed = order.is_prepayed()
		color = self.app.equipment.color_logic.get_color_name(order.color_id)

		status = ''
		if order.status == 'validate':
			status = 'Ожидание дизайнера'
		elif order.status == 'validated':
			status = 'Ожидание действий клиента'
		elif order.status == 'prepayed':
			status = 'Выполняется'
		elif order.status == 'no_spools':
			status = 'Приостановлен (отсутствует пластик)'

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
		if order.color_id != 0:
			text += f'Цвет изделия: {color.lower()}\n'
		if order.time > 0:
			text += f'Длительность печати'
			if order.time > 119: # if 2 hours or more show only hours amount
				text += f' (часов): {int(order.time/60)}\n'
			else:
				text += f': {int(order.time)} минут\n'
		ready = order.completion_estimate_date()
		if ready != None:
			text += f'Дата готовности (примерно): {ready}'
		if order.support_remover != '':
			text += f'Удаление поддержек: {order.support_remover.lower()}\n'
		if order.prepayed > 0:
			if not free_start and not prepayed:
				text += f'Предоплачено: {int(order.prepayed)}/{int(prepay_price)} рублей'
			else:
				text += f'Предоплачено: {int(order.prepayed)} рублей'

		# set buttons
		buttons = []
		if not self.is_admin():
			# order.color_id = ''
			# status = 'validated'
			if order.status == 'validated':
				if order.color_id == 0:
					buttons.append(['Выбрать цвет', 'color'])
				elif order.support_remover == '' and order.support_time > 0:
					buttons.append(['Выбрать кто уберет поддержки', 'supports'])
				elif settings_set:
					# Условия принятия заказа без предоплаты:
					# 1) Стоимость заказа меньше лимита
					# 2) Стоимость заказа меньше половины стоимости выполненных заказов
					if free_start:
						buttons.append(['Подтвердить и передать на выполнение', 'continue'])
					else:
						if prepayed:
							buttons.append(['Оплатить полностью', 'pay'])
						else:
							buttons.append(['Внести предоплату', 'pay'])

		buttons.append(['Отменить заказ'])
		buttons.append(['Назад'])
		self.GUI.tell_document_buttons(order.model_file, text, buttons, buttons, 1, order.order_id)

	def show_supports(self):
		text = 'Вы хотите убрать поддержки самостоятельно? Цена заказа будет меньше на ' + self.order.get_supports_price() + ' рублей'
		buttons = [['Да, уберу сам', 'Клиент'], ['Нет, уберите вы', 'Компания'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, self.order.order_id)

	def show_pay(self):
		order = self.order
		order.set_pay_code()

		if order.is_prepayed():
			price = order.price
		else:
			price = order.get_prepayment_price()

		text = 'Для оплаты сделайте перевод на карту сбербанка по номеру телефона, карточки или счета, указанных ниже. В комментарии обязательно укажите код заказа: '
		text += order.pay_code
		self.GUI.tell(text)
		self.GUI.tell('Сумма перевода: ' + str(int(price)))
		self.GUI.tell('Получатель перевода: ' + self.app.settings.get('transfer_receiver'))
		self.GUI.tell(self.app.settings.get('phone_number'))
		self.GUI.tell(self.app.settings.get('card_number'))
		self.GUI.tell(self.app.settings.get('account_number'))
		text = 'Для зачисления средств может понадобиться несколько минут. После зачисления средств вам прийдет уведомление о принятии заказа в работу.'
		buttons = [['Предоплату сделал', 'prepayed']]
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 3, order.order_id)

	def show_cancel_confirmation(self):
		text = 'Подтвердите отмену заказа'
		buttons = [['Да, подтверждаю', 'confirm'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.order_id)

	def show_confirmed_by_designer(self, order):
		text = f'Оценка заказа {order.name} выполнена'
		buttons = [['Перейти к заказу', 'now'], ['Перейти к заказу попозже', 'then']]
		message = self.GUI.tell_buttons(text, buttons, buttons, 5, order.order_id)
		message.general_clear = False
		message.order_id = order.order_id

	def show_rejected_by_designer(self, order, reason):
		text = f'Заказ {order.name} не прошел оценку.'
		if reason != '':
			text +=  f'Причина: {reason}'
		self.GUI.tell(text)

	def show_reject_reason(self):
		self.order_waiting = self.order
		self.chat.set_context(self.address, 6)
		self.GUI.tell_buttons('Напишите причину отказа', [['Не уточнять причину', 'none']], [], 6, self.order.order_id)

	def show_rejected_by_admin(self, order, reason):
		text = ''
		if reason != '':
			text = f' по причине: {reason}'
		text = f'Заказ {order.name} отменен администратором' + text
		self.GUI.tell(text)

	def show_material_unavailable(self, order):
		text = f'Заказ {order.name}\n\n'
		text += 'К сожалению в настоящее время на складе отсутствует нужный вам тип пластика. '
		text += 'Мы вам сообщим когда он будет в наличии.'
		self.GUI.tell(text)

	def show_booking_canceled(self, order):
		text = f'Предоплата заказа "{order.name}" не выполнена в срок. Бронь материала отменена'
		self.GUI.tell(text)

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
		elif data == 'pay':
			self.show_pay()
		elif data == 'Отменить заказ':
			if self.is_admin():
				self.show_reject_reason()
			else:
				self.show_cancel_confirmation()
		elif data == 'Назад':
			if self.is_admin():
				self.chat.user.admin.last_data = ''
				self.chat.user.admin.show_orders()
			else:
				self.chat.user.last_data = ''
				self.chat.user.show_orders()

	def process_supports(self):
		self.order.support_remover = self.message.btn_data
		self.order.set_price()
		self.app.db.update_order(self.order)
		self.show_order()

	def process_pay(self):
		# data = self.message.btn_data
		# if data == 'prepayed':
		# 	x = ''
		# elif data == 'Назад':
		# 	x = ''
		self.show_order()

	def process_reject_reason(self):
		if self.message.btn_data == 'none':
			self.reject_reason = ''
		else:
			self.reject_reason = self.message.text
		self.show_cancel_confirmation()

	def process_cancel_confirmation(self):
		if self.message.btn_data == 'confirm':
			if self.is_admin():
				for chat in self.app.chats:
					if chat.user_id == self.order.user_id:
						chat.user.client_order.show_rejected_by_admin(self.order, self.reject_reason)
						self.reject_reason = ''
			self.order.remove_reserve()
			self.app.orders.remove(self.order)
			self.app.db.remove_order(self.order)
			self.order = None
			self.chat.user.last_data = ''
			self.chat.user.show_orders()
			if self.order.status == 'validated':
				chat = self.app.get_chat(self.order.user_id)
				chat.user.penalty()
			return
		self.show_order()

	def process_confirmed_by_designer(self):
		if self.message.btn_data == 'now':
			self.show_order()

#---------------------------- LOGIC ----------------------------

	def is_admin(self):
		return self.chat.is_employee and 'Администратор' in self.chat.user.roles

	# TODO: create function to receive transfer from client. If prepayment is successful set client.orders_canceled to 0.