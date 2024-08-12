import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Color import Client_color
from lib.order.Text import Order_text
from lib.order.Edit import Edit
from lib.order.gcode.GUI import Gcode_gui
from datetime import date
import time

class Order_GUI:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.client_color = Client_color(app, chat, address + '/1')
		self.order_text = Order_text(app, chat)
		self.edit = Edit(app, chat, address + '/2')
		self.gcode_gui = Gcode_gui(app, chat, address + '/3')
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
			elif file == '3':
				self.gcode_gui.new_message(message)
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
				elif function == '9':
					self.process_say()
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
		order = self.order
		text = self.order_text.get_text(order)

		logical = order.logical_status
		physical = order.physical_status
		
		buttons = []
		if self.chat.is_admin():
			buttons.append(['Файлы gcode','gcode'])
			buttons.append(['Редактировать заказ','edit'])
			buttons.append(['Написать клиенту','say'])
			buttons.append(['Попросить перейти в чат', 'chat'])
			buttons.append(['Отменить заказ','reject'])
		elif self.chat.is_designer():
			if order.designer_id:
				if order.type in ['stl','link']:
					buttons.append(['Модель пригодна к 3д печати','accept'])
				elif order.type in ['sketch','item']:
					if order.logical_status == 'prevalidate':
						buttons.append(['Примерное понимание заказа сформировано','accept'])
				if order.type == 'item' and order.logical_status == 'waiting_for_design':
						buttons.append(['Моделирование и слайсинг выполнены','accept'])
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

		text = 'Для оплаты сделайте перевод на карту сбербанка по номеру карточки. ОБЯЗАТЕЛЬНО укажите код перевода в сообщении получателю.\n\n'
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
		text = f'Оценка заказа "{order.name}" выполнена'
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

	def show_say(self):
		self.chat.set_context(self.address, 9)
		text = 'Напишите сообщение клиенту'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 9, self.order.id)

#---------------------------- PROCESS ----------------------------

	def process_order(self):
		data = self.message.btn_data
		if self.chat.is_admin():
			if data == 'Назад':
				self.chat.user.admin.last_data = ''
				self.chat.user.admin.show_orders()
			elif data == 'gcode':
				self.gcode_gui.order = self.order
				self.gcode_gui.last_data = ''
				self.gcode_gui.first_message(self.message)
			elif data == 'edit':
				self.edit.first_message(self.message)
			elif data == 'say':
				self.show_say()
			elif data == 'chat':
				chat = self.app.get_chat(self.order.user_id)
				chat.user.show_redirect_to_chat(self.order)
				self.last_data = ''
				self.show_order()
			elif data == 'reject':
				self.show_reject_reason()
		elif self.chat.is_designer():
			if data == 'take':
				self.order.designer_id = self.chat.user_id
				self.app.db.update_order(self.order)
				self.show_order()
			elif data == 'accept':
				self.chat.user.designer.general.order = self.order
				self.chat.user.designer.general.last_data = ''
				self.chat.user.designer.general.order_accepted()
			elif data == 'chat':
				chat = self.app.get_chat(self.order.user_id)
				chat.user.show_redirect_to_chat(self.order)
				self.order.miscellaneous += '\nЗаказ переведен в чат'
				self.last_data = ''
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

	def process_say(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_clarify()
		else:
			text = f'Сообщение от администратора: {self.message.text}'
			self.GUI.tell_id(self.order.user_id, text)
			self.show_order()

#---------------------------- LOGIC ----------------------------

