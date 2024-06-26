import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Color import Client_color
import time
import random

class Order_GUI:
	address = ''
	
	app = None
	chat = None
	message = None
	order = None
	order_waiting = None
	GUI = None
	context = ''
	color = None
	last_data = ''

	order = None

	client_color = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.client_color = Client_color(app, chat, address + '/1')

	def first_message(self, message):
		self.message = message
		self.set_order()
		self.show_order()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		self.set_order()
		self.GUI.clear_order_chat(self.order.id)

		data = message.data
		function = message.function
		if message.data_special_format:
			if message.file3 == '' and (data == '' or data != self.last_data):	# process user button presses and skip repeated button presses
				self.last_data = data
				if function == '1':
					self.process_order()
				elif function == '2':
					self.process_supports()
				elif function == '3':
					self.process_pay()
				elif function == '4':
					self.process_cancel_confirmation()
				elif function == '5':
					self.process_confirmed_by_designer()
				elif function == '6':
					self.process_reject_reason()
			elif message.file3 == '1':
				self.client_color.new_message(message)
		if message.type == 'text':
			self.GUI.messages_append(message)

	def set_order(self):
		try:
			order_id = int(self.message.instance_id)
			for order in self.app.orders:
				if order.id == order_id:
					self.order = order
					return
		except:
			if self.order_waiting != None:
				self.order = self.order_waiting
				self.order_waiting = None

#---------------------------- SHOW ----------------------------

	def show_order(self):
		text = self.get_text()
		order = self.order

		logical = order.logical_status
		physical = order.physical_status
		
		buttons = []
		if self.is_admin():
			x = ''
			# TODO: put buttons for admin
		else:
			if not order.type == 'production':
				# Уборка поддержек и выбор цвета
				if logical == 'validated':
					# TODO: if type == 'sketch' ask client to confirm photos, else: create dialog with client for clarification.
					if (order.support_time and 
						not order.support_remover):
						buttons.append(['Выбрать кто уберет поддержки', 'supports'])
					elif not order.color:
							buttons.append(['Выбрать цвет', 'color'])
				# Предоплата
				elif logical == 'parameters_set':
					buttons.append(['Внести предоплату', 'pay'])
				elif physical in ['in_line','printing','finished','in_pick-up'] and not order.is_payed():
					buttons.append(['Оплатить полностью', 'pay'])
				# Отмена заказа
				if (    (order.type in ['stl','link']    and physical in ['prepare','in_line']) or 
					not (order.type in ['sketch','item'] and order.assinged_designer_id)):
					buttons.append('Отменить заказ')
		buttons.append('Назад')

		# show order and buttons
		if type_ == 'stl':
			self.GUI.tell_document_buttons(order.model_file, text, buttons, buttons, 1, order.id)
		elif type_ == 'link':
			self.GUI.tell_link_buttons(order.link, text, buttons, buttons, 1, order.id)
		elif type_ == 'sketch' or type_ == 'item':
			for file in order.sketches:
				self.GUI.tell_file(file[0], file[1], '')
			self.GUI.tell_buttons(text, buttons, buttons, 1, order.id)

	def show_supports(self):
		text = 'Вы хотите убрать поддержки самостоятельно? Цена заказа будет меньше на ' + str(self.order.get_supports_price()) + ' рублей'
		buttons = [['Да, уберу сам', 'Клиент'], ['Нет, уберите вы', 'Компания'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, self.order.id)

	def show_pay(self):
		order = self.order
		order.set_pay_code()

		if order.is_prepayed():
			price = order.price
		else:
			price = order.get_prepayment_price()

		text = 'Для оплаты сделайте перевод на карту сбербанка по номеру телефона, карточки или счета, указанных ниже. В комментарии обязательно укажите код заказа: '
		text += str(order.pay_code)
		self.GUI.tell(text)
		self.GUI.tell('Сумма перевода: ' + str(int(price)))
		self.GUI.tell('Получатель перевода: ' + self.app.settings.get('transfer_receiver'))
		self.GUI.tell(self.app.settings.get('phone_number'))
		self.GUI.tell(self.app.settings.get('card_number'))
		self.GUI.tell(self.app.settings.get('account_number'))
		text = 'Для зачисления средств может понадобиться несколько минут.'
		text += ' После зачисления средств вам прийдет уведомление о принятии заказа в работу.'
		text += ' В случае если ваш перевод не привязался к заказу напишите в поддержку.'
		buttons = [['Предоплату сделал', 'prepayed']]
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 3, order.id)

	def show_cancel_confirmation(self):
		text = 'Подтвердите отмену заказа'
		buttons = [['Да, подтверждаю', 'confirm'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.id)

	def show_confirmed_by_designer(self, order):
		text = f'Оценка заказа {order.name} выполнена'
		buttons = [['Перейти к заказу', 'now'], ['Перейти к заказу попозже', 'then']]
		message = self.GUI.tell_buttons(text, buttons, buttons, 5, order.id)
		message.general_clear = False

	def show_rejected_by_designer(self, order, reason):
		text = f'Заказ "{order.name}" не прошел оценку.'
		if reason != '':
			text +=  f'\nПричина: {reason}'
		self.GUI.tell(text)

	def show_reject_reason(self):
		self.order_waiting = self.order
		self.chat.set_context(self.address, 6)
		self.GUI.tell_buttons('Напишите причину отказа', [['Не уточнять причину', 'none']], [], 6, self.order.id)

	def show_rejected_by_admin(self, order, reason):
		text = ''
		if reason != '':
			text = f' по причине: {reason}'
		text = f'Заказ "{order.name}" отменен администратором' + text
		self.GUI.tell(text)

	def show_material_unavailable(self, order):
		text = f'Заказ "{order.name}"\n\n'
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
			self.client_color.last_data = ''
			self.client_color.first_message(self.message)
		elif data == 'supports':
			self.show_supports()
		elif data == 'continue':
			if type_ == 'stl' or type_ == 'link':
				self.order.physical_status = 'in_line'
			self.order.logical_status = 'prepayed'
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
						chat.user.order_GUI.show_rejected_by_admin(self.order, self.reject_reason)
						self.reject_reason = ''
			if self.order.logical_status == 'validated':
				chat = self.app.get_chat(self.order.user_id) # if admin is looking at order
				chat.user.penalty()
			self.order.remove_reserve()
			self.app.orders.remove(self.order)
			self.app.db.remove_order(self.order)
			self.order = None
			self.chat.user.last_data = ''
			if self.is_admin():
				self.chat.user.admin.last_data = ''
				self.chat.user.admin.show_orders()
			else:
				self.chat.user.last_data = ''
				self.chat.user.show_orders()
		else:
			self.show_order()

	def process_confirmed_by_designer(self):
		if self.message.btn_data == 'now':
			self.show_order()

#---------------------------- LOGIC ----------------------------

	def is_admin(self):
		return self.chat.is_employee and 'Администратор' in self.chat.user.roles

	def get_text(self):
		order = self.order

		# set parameters
		free_start = order.is_free_start()
		prepayed = order.is_prepayed()
		color = self.app.equipment.color_logic.get_color_name(order.color_id)
		plastic_type = order.plastic_type
		if plastic_type == 'basic':
			plastic_type = 'любой базовый'
		plastic_type.lower()

		# convert order status to readable format
		status = ''
		delivery_text = ''
		logical = order.logical_status
		physical = order.physical_status
		if logical in ['prevalidate','validate'] or order.assinged_designer_id:
			status = 'Ожидание дизайнера'
		elif logical == 'validated':
			status = 'Ожидание действий клиента'
		elif logical == 'parameters_set':
			status = 'Ожидание оплаты'
		# statuses for item order
		elif logical == 'waiting_for_item':
			status = 'Принесите предмет в пункт выдачи'
			delivery_text = 'Код передачи'
		elif logical in ['sample_aquired','waiting_for_design']:
			status = 'Ожидание дизайнера'
		# physical statuses
		elif physical == 'in_line':
			status = 'В очереди на печать'
		elif physical == 'printing':
			status = 'Печатается'
		elif physical == 'finished':
			status = 'Печать завершена'
		elif physical == 'in_pick-up':
			status = 'В пункте выдачи'
			delivery_text = 'Код получения'

		# set text
		text = order.name + '\n\n'
		if status:
			text += f'Статус: {status.upper()}\n'
		if order.delivery_code and delivery_text:
			text += f'{delivery_text}: {order.delivery_code}\n\n'
		text += f'Дата создания: {self.app.functions.russian_date(order.date)}\n'
		if order.price:
			text += f'Стоимость: {order.price} рублей\n'
		if order.quantity:
			text += f'Кол-во экземпляров: {order.quantity}\n'
		if order.weight:
			text0 = 'Общий вес' if order.quantity else 'Вес'
			text += f'{text0}: {int(order.weight) * order.quantity} грамм\n'
		if plastic_type:
			text += f'Тип материала: {plastic_type}\n'
		if order.color_id:
			text += f'Цвет изделия: {color.lower()}\n'
		if order.completion_date:
			date = self.app.functions.russian_date(order.completion_date)
			text += f'Дата готовности (примерно): {date}'
		if order.support_time:
			text += f"Удаление поддержек: {'клиент' if order.support_remover == 'Клиент' else 'студия'}\n"
		if order.payed:
			if not free_start and not prepayed:
				text += f'Предоплачено: {int(order.payed)}/{int(prepay_price)} рублей'
			else:
				text += f'Предоплачено: {int(order.payed)} рублей'
		return text