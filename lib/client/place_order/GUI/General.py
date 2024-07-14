import sys
sys.path.append('../lib')
from lib.Gui import Gui
from datetime import datetime
import time

class General_parameters:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.order = None
		self.GUI = Gui(app, chat, address)

	def first_message(self, message):
		self.order = self.chat.user.order
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		function = message.function
		if message.data_special_format:
			if self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				elif function == '2':
					self.process_quality()
				elif function == '3':
					self.process_name()
				elif function == '4':
					self.process_comment()
				elif function == '5':
					self.process_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'Сколько экземпляров вам нужно?'
		buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
		self.GUI.tell_buttons(text, buttons, ['1', '2'], 1, self.order.id)

	def show_quality(self):
		text = 'Какое качество печати вам нужно? В зависимости от особенностей модели разница в стоимости печати может достигать 2.5 раза (для максимальной прочности).'
		buttons = [['максимально дешевое', 'cheap'], ['оптимальное цена/качество','optimal'], ['максимальное качество', 'quality'], ['максимальная прочность', 'durability']]
		self.GUI.tell_buttons(text, buttons, [], 2, self.order.id)

	def show_name(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Напишите название для вашего заказа')

	def show_comment(self):
		self.chat.set_context(self.address, 4)
		buttons = [['Комментариев к заказу не имею', 'none']]
		self.GUI.tell_buttons('Напишите комментарий', buttons, [], 4, self.order.id)

	def show_confirmation(self):
		text = ''
		if self.order.type == 'sketch':
			text = 'Ваши дальнейшие действия по заказу:\n'
			text += '1) Дождаться результатов предварительной оценки,\n'
			text += '2) Выбрать желаемый цвет изделия и внести предоплату,\n'
			text += '3) Дождаться разработки модели и подтвердить ее соответствие вашим ожиданиям (при необходимости запросив корректировку),\n'
			text += '4) Ожидать исполнения заказа.\n'
		elif self.order.type == 'item':
			text = 'Ваши дальнейшие действия по заказу:\n'
			text += '1) Дождаться результатов предварительной оценки,\n'
			text += '2) Выбрать желаемый цвет изделия и внести предоплату,\n'
			text += '3) Принести предмет в пункт выдачи (адрес указан в разделе информации),\n'
			text += '4) Ожидать исполнения заказа.\n'
		self.GUI.tell(text)
		start_date = self.app.order_logic.get_completion_date(0, '*')
		start_day = self.app.functions.russian_date(start_date)
		text = 'Ожидаемый срок запуска в печать: ' + start_day
		self.GUI.tell(text)
		text = 'Подтвердите создание заказа'
		buttons = [['Подтверждаю', 'confirm'], ['Удалить заказ', 'remove']]
		self.GUI.tell_buttons(text, buttons, buttons, 5, self.order.id)

	def show_name_used(self):
		self.GUI.tell('Введенное название уже используется для другого вашего заказа')

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		try:
			self.order.quantity = int(self.message.btn_data)
			self.show_quality()
		except:
			self.show_top_menu()

	def process_quality(self):
		if self.message.btn_data == '':
			self.show_quality()
		self.order.quality = self.message.btn_data
		self.show_name()

	def process_name(self):
		text = self.message.text
		if self.app.order_logic.is_unique_name(self.chat.user_id, text):
			self.chat.context = ''
			self.order.name = text
			self.show_comment()
		else:
			self.show_name_used()
			time.sleep(3)
			self.show_name()

	def process_comment(self):
		self.chat.context = ''
		if self.message.btn_data != 'none':
			self.order.comment = self.message.text
		else:
			self.order.comment = ''
		self.show_confirmation()

	def process_confirmation(self):
		# self.message.file_name = 'hi.stl'
		# self.message.file_id = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'
		# self.message.type = 'document'
		# self.order.name = 'название модели'
		# self.order.quality = 'В доме'
		# self.order.quantity = 3

		data = self.message.btn_data
		if data == 'confirm':
			self.order.date = datetime.today()
			if self.order.type in ['sketch','item']:
				self.order.logical_status = 'prevalidate'
			else:
				self.order.logical_status = 'validate'
			if self.order.type == 'sketch':
				self.order.confirmed = False
			self.order.user_id = self.app.chat.user_id
			self.app.orders_append(self.order)
			self.app.db.create_order(self.order)
			self.chat.user.show_wait_for_designer()
			for chat in self.app.chats:
				if chat.is_employee and 'Дизайнер' in chat.user.roles:
					chat.user.designer.show_new_order(self.order)
		self.chat.user.reset_order()
		self.chat.user.show_top_menu()

		# self.GUI.tell_document('BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ', 'this is caption text')