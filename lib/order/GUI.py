import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Color import Client_color
from lib.order.Edit import Edit
from datetime import date
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
				elif function == '7':
					self.process_clarify()
				elif function == '8':
					self.process_clarify_reason()
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
			# TODO: add tell client functionality
			buttons.append(['Отменить заказ','reject'])
		elif self.chat.is_designer():
			if order.designer_id:
				if order.type in ['stl','link']:
					buttons.append(['Модель пригодна к 3д печати','accept'])
				elif order.type in ['sketch','item']:
					if order.logical_status == 'prevalidate':
						buttons.append(['Примерное понимание заказа сформировано','accept'])
				if order.type == 'sketch' and order.logical_status in ['waiting_for_design','clarify']:
					if order.confirmed:
						buttons.append(['Моделирование и слайсинг выполнены','accept'])
					else:
						buttons.append(['Согласовать модель с клиентом','client_check'])
						buttons.append(['Перевести в чат', 'chat'])
				elif order.type == 'production':
					buttons.append(['Редактировать заказ','edit'])
					buttons.append(['Перевести в чат', 'chat'])
					buttons.append(['Отказать','reject'])
			else:
				buttons.append(['Взять в работу', 'take'])
		elif not self.chat.is_employee:
			if order.type == 'production':
				x = '' # show only 'Назад' button
			else:
				# Уборка поддержек и выбор цвета
				if logical == 'validated':
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
				if order.type == 'sketch' and order.logical_status == 'client_check' and not order.confirmed:
					buttons.append(['Проверить модель', 'client_check'])
				# Отмена заказа
				if ((order.type in ['stl', 'link'] and physical in ['prepare', 'in_line']) or 
				    (order.type in ['sketch', 'item'] and not order.designer_id)):
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
		text = 'Вы хотите убрать поддержки самостоятельно? '
		price = self.order.get_supports_price()
		if (price >= 100 and price < 10000) or self.order.price <= 1000:
			text += f'Цена заказа будет меньше на {price} рублей.'
		else:
			text += 'Цена заказа может снизится.'
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
		buttons = [['Перейти к заказу', 'now']]
		message = self.GUI.tell_buttons(text, buttons, buttons, 5, order.id)
		message.general_clear = False

	def show_rejected_by_designer(self, order, reason):
		text = f'Заказ "{order.name}" не прошел оценку.'
		if reason != '':
			text +=  f'\nПричина: {reason}'
		self.GUI.tell(text)

	def show_reject_reason(self):
		self.chat.set_context(self.address, 6)
		self.order_waiting = self.order
		self.GUI.tell_buttons('Напишите причину отказа', [['Не уточнять причину', 'none']], [], 6, self.order.id)

	def show_clarify(self):
		text = 'Подтвердите соответствие разработанной модели вашим чертежам'
		for screenshot in self.order.screenshots:
			self.GUI.tell_photo('', screenshot)
		buttons = [['Подтверждаю','confirm']]
		buttons.append(['Не соответствует, нужна доработка','clarify'])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 7, self.order.id)

	def show_clarify_reason(self):
		self.chat.set_context(self.address, 8)
		text = 'Напишите что в модели не соответствует чертежам'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 8, self.order.id)

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
				self.order.designer_id = self.chat.user_id
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
			elif data == 'client_check':
				self.chat.user.designer.show_screenshots(self.order)
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
			elif data == 'client_check':
				self.show_clarify()

	def process_supports(self):
		self.order.support_remover = self.message.btn_data
		self.order.set_price()
		self.app.db.update_order(self.order)
		self.show_order()

	def process_pay(self):
		self.show_order()

	def process_reject_reason(self):
		self.chat.context = ''
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

	def process_clarify(self):
		order = self.order
		data = self.message.btn_data
		if data == 'Назад':
			self.show_order()
		elif data == 'confirm':
			order.logical_status = 'waiting_for_design'
			order.confirmed = True
			self.app.db.update_order(order)
			chat = self.app.get_chat(order.designer_id)
			chat.user.designer.show_design_confirmed(order)
			self.show_order()
		elif data == 'clarify':
			self.show_clarify_reason()

	def process_clarify_reason(self):
		self.chat.context = ''
		data = self.message.btn_data
		if data == 'Назад':
			self.show_clarify()
		else:
			text = self.message.text
			chat = self.app.get_chat(self.order.designer_id)
			chat.user.designer.show_clarify(self.order, text)
			now = date.today()
			if now == self.order.created:
				text = f'\nУточнение: {text}'
			else:
				text = f'\nУточнение ({self.app.functions.clean_date(now)}): {text}'
			self.order.miscellaneous += text
			self.order.logical_status = 'clarify'
			self.app.db.update_order(self.order)
			self.show_order()

#---------------------------- LOGIC ----------------------------

	def get_text(self):
		order = self.order
		data = self.app.data

		# set parameters
		free_start = order.is_free_start()
		prepayed = order.is_prepayed()
		
		# convert order status to readable format
		status = order.logical_status
		if not status:
			status = order.physical_status
		delivery_text = 'Код передачи/получения'
		if self.chat.is_employee:
			status = data.statuses[status]
		else:
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
			elif logical == 'client_check':
				status = 'Ожидание действий клиента'
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
			else:
				status = data.statuses[status]

		# TODO: process situations when functions may retull null
		# prepare data
		name = order.name
		id = order.id
		status = status.upper()
		delivery_code = order.delivery_code
		created = self.app.functions.russian_date(order.created)
		price = order.price
		quantity = order.quantity
		quality = data.quality[order.quality]
		weight = int(order.weight) * quantity
		total_weight = int(order.weight) * quantity
		plastic_type = order.plastic_type
		if plastic_type == 'basic':
			plastic_type = 'любой базовый'
		plastic_type.lower()
		color_id = order.color_id
		color = self.app.equipment.color_logic.get_color_name(order.color_id)
		if color:
			color = color.lower()
		completion_date = self.app.functions.russian_date(order.completion_date)
		support_time = int(order.support_time)
		support_remover = 'клиент' if order.support_remover == 'Клиент' else 'студия'
		payed = int(order.payed)
		prepayment_price = int(order.get_prepayment_price())
		if payed:
			if not free_start and not prepayed:
				prepayed = f'Предоплачено: {payed}/{prepayment_price} рублей'
			else:
				prepayed = f'Предоплачено: {payed} рублей'
		else:
			prepayed = 'Предоплачено: 0 рублей'
		comment = order.comment
		chat = self.app.get_chat(order.user_id)
		user_name = chat.user_name
		user_id = chat.user_id
		type_ = data.types[order.type]
		priority = order.priority
		confirmed = ''
		if order.type == 'sketch':
			confirmed = 'нет'
			if order.confirmed:
				confirmed = 'да'
		designer_user_name = self.app.get_chat(order.designer_id)
		if designer_user_name:
			designer_user_name = designer_user_name.user_name
		printer_type_name = self.app.printer_type_logic.get_printer_type(order.printer_type)
		if printer_type_name:
			printer_type_name = printer_type_name.name
		layer_height = order.layer_height
		model_file = order.model_file
		link = order.link
		sketches = len(order.sketches)
		prepayment_percent = int(order.prepayment_percent)
		pay_code = order.pay_code
		delivery_user_name = self.app.get_chat(order.delivery_user_id)
		if delivery_user_name:
			delivery_user_name = delivery_user_name.user_name
		miscellaneous = order.miscellaneous

		# set admin text
		if self.chat.is_admin():
			text = f'{id}: {name}\n\n'
			text += f'Клиент: {user_name} (id: {user_id})\n'
			text += '\n--- Общие ---\n'
			text += f'Тип заказа: {type_}\n'
			text += f'Статус: {status}\n'
			text += f'Комментарий: {comment}\n'
			text += f'Приоритет: {priority}\n'
			if confirmed:
				text += f'Подтвержден клиентом: {confirmed}\n'
			text += f'Дата готовности (примерно): {completion_date}\n'
			text += f'Кол-во экземпляров: {quantity}\n'
			text += f'Качество: {quality}\n'
			text += f'Вес экземпляра: {weight} грамм\n'
			text += f'Цвет изделия: {color}\n'
			text += f'Назначенный дизайнер: {designer_user_name}\n'
			text += f'Дополнительная информация: {miscellaneous}\n'
			text += '\n--- Настройки печати ---\n'
			text += f'Тип материала: {plastic_type}\n'
			text += f'Тип принтера: {printer_type_name}\n'
			text += f'Высота слоя: {layer_height}\n'
			text += '\n--- Файлы, ссылка, фото ---\n'
			if model_file:
				text += 'stl файл: 1\n'
			else:
				text += 'stl файл: 0\n'
			if link:
				text += 'Ссылка: 1\n'
			else:
				text += 'Ссылка: 0\n'
			text += f'Чертежы/фото: {sketches}\n'
			text += '\n--- Финансы ---\n'
			text += f'Стоимость: {price} рублей\n'
			text += f'{prepayed}\n'
			text += f'Время удаления поддержек c 1 шт.: {support_time}\n'
			text += f'Процент предоплаты: {prepayment_percent}\n'
			text += f"Удаление поддержек: {support_remover}\n"
			text += '\n--- Доставка ---\n'
			text += f'Код оплаты: {pay_code}\n'
			text += f'{delivery_text}: {delivery_code}\n\n'
			text += f'Точка выдачи: {delivery_user_name}\n'

		# set designer text
		elif self.chat.is_designer():
			text = f'{id}: {name}\n\n'
			text += f'Тип заказа: {type_}\n'
			text += f'Статус: {status}\n'
			text += f'Дата создания: {created}\n'
			if priority:
				text += f'Приоритет: {priority}\n'
			if color_id:
				text += f'Цвет изделия: {color}\n'
			if quantity > 1:
				text += f'Кол-во экземпляров: {quantity}\n'
			text += f'Качество: {quality}\n'
			if printer_type_name:
				text += f'Тип принтера: {printer_type_name}\n'
			if plastic_type:
				text += f'Тип материала: {plastic_type}\n'
			if weight:
				text += f'Вес экземпляра: {weight} грамм\n'
			if layer_height:
				text += f'Высота слоя: {layer_height}\n'
			if support_time:
				text += f'Время удаления поддержек c 1 шт.: {support_time}\n'
			if comment:
				text += f'Комментарий: {comment}\n'
			if miscellaneous:
				text += f'Дополнительная информация: {miscellaneous}\n'
		
		# set client text
		elif not self.chat.is_employee:
			text = ''
			text = name + '\n\n'
			text += f'Статус: {status}\n'
			if delivery_code and delivery_text:
				text += f'{delivery_text}: {delivery_code}\n\n'
			text += f'Дата создания: {created}\n'
			if priority:
				text += f'Приоритет: {priority}\n'
			if price:
				text += f'Стоимость: {price} рублей\n'
			if quantity > 1:
				text += f'Кол-во экземпляров: {quantity}\n'
			text += f'Качество: {quality}\n'
			if total_weight:
				text0 = 'Общий вес' if quantity else 'Вес'
				text += f'{text0}: {total_weight} грамм\n'
			if plastic_type:
				text += f'Тип материала: {plastic_type}\n'
			if color_id:
				text += f'Цвет изделия: {color}\n'
			if completion_date:
				text += f'Дата готовности (примерно): {completion_date}\n'
			if support_time:
				text += f"Удаление поддержек: {support_remover}\n"
			if prepayed:
				text += f'{prepayed}\n'
			if comment:
				text += f'Комментарий: {comment}\n'
		return text