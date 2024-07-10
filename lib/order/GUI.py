import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Color import Client_color
from lib.order.Edit import Edit
import time
import random

class Order_GUI:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.client_color = Client_color(app, chat, address + '/1')
		self.edit = Edit(app, chat, address + '/2')
		self.message = None
		self.order = None
		self.order_waiting = None
		self.color = None

	def first_message(self, message):
		self.message = message
		self.set_order()
		self.show_order()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		self.set_order()
		self.GUI.clear_order_chat(self.order.id)

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				self.client_color.new_message(message)
			elif file == '2':
				self.edit.new_message(message)
			elif self.chat.not_repeated_button(self):
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
		self.chat.add_if_text(self)

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
		# order.logical_status = 'validated' # TODO: remove for production!

		logical = order.logical_status
		physical = order.physical_status
		
		buttons = []
		if self.chat.is_admin():
			buttons.append(['Редактировать заказ','edit'])
			buttons.append(['Отменить заказ','reject'])
		elif self.chat.is_designer():
			if order.type == 'production':
				if order.assigned_designer_id:
					buttons.append(['Редактировать заказ','edit'])
					buttons.append(['Перевести в чат', 'chat'])
					buttons.append(['Отказать','reject'])
				else:
					buttons.append(['Взять в работу', 'take'])
			else:
				buttons.append(['Принять заказ','accept'])
		elif not self.chat.is_employee:
			if order.type == 'production':
				x = '' # show only 'Назад' button
			else:
				# Уборка поддержек и выбор цвета
				if logical == 'validated':
					# TODO: if type == 'sketch' ask client to confirm photos, else: create dialog with client for clarification.
					if (order.support_time and 
						not order.support_remover):
						buttons.append(['Выбрать кто уберет поддержки', 'supports'])
					elif not order.color_id:
							buttons.append(['Выбрать цвет', 'color'])
				# Предоплата
				elif logical == 'parameters_set':
					if order.price == order.get_prepayment_price():
						buttons.append(['Оплатить заказ', 'pay'])
					else:
						buttons.append(['Внести предоплату', 'pay'])
				elif physical in ['in_line','printing','finished','in_pick-up'] and not order.is_payed() and order.is_prepayed():
					buttons.append(['Оплатить оставшуюся часть', 'pay'])
				# Отмена заказа
				if ((order.type in ['stl', 'link'] and physical in ['prepare', 'in_line']) or 
				    (order.type in ['sketch', 'item'] and not order.assigned_designer_id)):
				    buttons.append('Отменить заказ')
		buttons.append('Назад')

		# show
		type_ = order.type
		if type_ == 'stl':
			self.GUI.tell_document(order.model_file, '')
			self.GUI.tell_buttons(text, buttons, buttons, 1, order.id)
		elif type_ == 'link':
			self.GUI.tell_link_buttons(order.link, text, buttons, buttons, 1, order.id)
		elif type_ == 'sketch' or type_ == 'item':
			for file in order.sketches:
				self.GUI.tell_file(file[0], file[1], '')
			self.GUI.tell_buttons(text, buttons, buttons, 1, order.id)
		elif type_ == 'production':
			self.GUI.tell_buttons(text, buttons, buttons, 1, order.id)

	def show_supports(self):
		text = 'Вы хотите убрать поддержки самостоятельно? Цена заказа будет меньше на ' + str(self.order.get_supports_price()) + ' рублей'
		buttons = [['Да, уберу сам', 'Клиент'], ['Нет, уберите вы', 'Компания'], 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, self.order.id)

	def show_pay(self):
		order = self.order
		order.set_pay_code()

		if order.is_prepayed():
			price = order.price - order.payed
		else:
			price = order.get_prepayment_price()

		setting = self.app.setting.get
		tell = self.GUI.tell

		text = 'Для оплаты сделайте перевод на карту сбербанка по номеру карточки. Обязательно укажите код перевода в сообщении получателю.\n\n'
		text += f'Код перевода: {order.pay_code}\n'
		text += f'Сумма перевода: {int(price)}\n'
		text += f'Получатель перевода: {setting("transfer_receiver")}\n'
		text += 'Номер карточки: ↓'
		tell(text)
		tell(setting('card_number'))

		text = 'После поступления средств вам прийдет уведомление.'
		text += ' В случае если уведомление не пришло напишите в поддержку указав название заказа и сумму перевода.'
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
		if self.chat.is_admin():
			if data == 'Назад':
				self.chat.user.admin.last_data = ''
				self.chat.user.admin.show_orders()
			elif data == 'edit':
				self.edit.first_message(self.message)
			elif data == 'reject':
				self.show_reject_reason()
		elif self.chat.is_designer():
			if data == 'take':
				self.order.assigned_designer_id = self.chat.user_id
				self.app.db.update_order(self.order)
				self.show_order()
			elif data == 'accept':
				self.chat.user.designer.general.last_data = ''
				self.chat.user.designer.general.order_accepted()
			elif data == 'chat':
				chat = self.app.get_chat(self.order.user_id)
				chat.user.show_redirect_to_chat(self.order)
				self.order.miscellaneous += '\nЗаказ переведен в чат'
				self.show_order()
			elif data == 'edit':
				self.edit.first_message(self.message)
			elif data == 'reject':
				self.show_reject_reason()
			elif data == 'Назад':
				self.chat.user.designer.general.last_data = ''
				self.chat.user.designer.general.show_top_menu()
		elif not self.chat.is_employee:
			if data == 'Назад':
				self.chat.user.last_data = ''
				self.chat.user.show_orders()
			elif data == 'reject':
				self.show_cancel_confirmation() # inform about payments
			elif data == 'color':
				self.client_color.last_data = ''
				self.client_color.first_message(self.message)
			elif data == 'supports':
				self.show_supports()
			elif data == 'pay':
				self.show_pay()

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
		order = self.order
		if self.message.btn_data == 'confirm':
			if self.chat.is_employee:
				for chat in self.app.chats:
					if chat.user_id == order.user_id:
						chat.user.order_GUI.show_rejected_by_admin(order, self.reject_reason)
						self.reject_reason = ''
			if order.logical_status == 'validated':
				chat = self.app.get_chat(order.user_id)
				chat.user.penalty()
			order.remove()
			order = None
			self.chat.user.last_data = ''
			if self.chat.is_employee:
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

	def get_text(self):
		order = self.order
		data = self.app.data

		# set parameters
		free_start = order.is_free_start()
		prepayed = order.is_prepayed()
		color = self.app.equipment.color_logic.get_color_name(order.color_id)
		plastic_type = order.plastic_type
		if plastic_type == 'basic':
			plastic_type = 'любой базовый'
		plastic_type.lower()

		# convert order status to readable format
		if self.chat.is_employee:
			status = order.logical_status
			if not status:
				status = order.physical_status
			status = data.statuses[status]
			delivery_text = 'Код передачи/получения'
		else:
			delivery_text = ''
			logical = order.logical_status
			physical = order.physical_status
			if logical in ['prevalidate','validate']:
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
		text += f'Дата создания: {self.app.functions.russian_date(order.created)}\n'
		if order.price:
			text += f'Стоимость: {order.price} рублей\n'
		if order.quantity > 1:
			text += f'Кол-во экземпляров: {order.quantity}\n'
		if order.quality:
			text += f'Качество: {data.quality[order.quality]}\n'
		if order.weight:
			text0 = 'Общий вес' if order.quantity else 'Вес'
			text += f'{text0}: {int(order.weight) * order.quantity} грамм\n'
		if plastic_type:
			text += f'Тип материала: {plastic_type}\n'
		if order.color_id:
			text += f'Цвет изделия: {color.lower()}\n'
		if order.completion_date:
			date = self.app.functions.russian_date(order.completion_date)
			text += f'Дата готовности (примерно): {date}\n'
		if order.support_time:
			text += f"Удаление поддержек: {'клиент' if order.support_remover == 'Клиент' else 'студия'}\n"
		if order.payed:
			if not free_start and not prepayed:
				text += f'Предоплачено: {int(order.payed)}/{int(order.get_prepayment_price())} рублей\n'
			else:
				text += f'Предоплачено: {int(order.payed)} рублей\n'
		if order.comment:
			text += f'Комментарий: {order.comment}\n'
		if self.chat.is_employee:
			chat = self.app.get_chat(order.user_id)
			text += f'Клиент: {chat.user_name} (id: {chat.user_id})\n'
			text += f'Тип заказа: {data.types[order.type]}\n'
			if order.priority:
				text += f'Приоритет: {order.priority}\n'
			if order.assigned_designer_id:
				designer = self.app.get_chat(order.assigned_designer_id)
				text += f'Назначенный дизайнер: {designer.user_name}\n'
			if order.printer_type:
				printer_type = self.app.printer_type_logic.get_printer_type(order.printer_type)
				text += f'Тип принтера: {printer_type.name}\n'
			if order.layer_height:
				text += f'Высота слоя: {order.layer_height}\n'
			if order.model_file:
				text += 'stl файл: 1\n'
			if order.link:
				text += 'Ссылка: 1\n'
			if order.sketches:
				text += f'Чертежы/фото: {len(order.sketches)}\n'
			if order.support_time:
				text += f'Время удаления поддержек c 1 шт.: {int(order.support_time)}\n'
			if order.prepayment_percent:
				text += f'Процент предоплаты: {int(order.prepayment_percent)}\n'
			if order.pay_code:
				text += f'Код оплаты: {order.pay_code}\n'
			if order.delivery_user_id:
				delivery = self.app.get_chat(order.delivery_user_id)
				text += f'Точка выдачи: {delivery.user_name}\n'
			if order.miscellaneous:
				text += f'Дополнительная информация: {order.miscellaneous}\n'
		return text