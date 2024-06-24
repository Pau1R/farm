import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.order.Order import Order
from lib.employee.designer.GUI.Gcode import Gcode_gui

class Stl_link:
	address = ''
	type = ''

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''

	order = None
	orders = []
	order_timer = ''

	weight = 1
	supports = False
	support_minutes = 0
	printer_type = ''
	material = ''
	price = 0

	gcode_gui = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.gcode_gui = Gcode_gui(app, chat, address + '/1', self)

	def first_message(self, message, type_):
		self.reset_values()
		self.type = type_
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format:
			if message.file4 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.process_top_menu()
				elif message.function == '2':
					self.process_validate()
				elif message.function == '3':
					self.process_accept()
				elif message.function == '4':
					self.process_plastic_type()
				# elif message.function == '5':
				# 	self.process_quantity()
				elif message.function == '5':
					self.process_weight()
				elif message.function == '6':
					self.process_supports()
				elif message.function == '7':
					self.process_confirmation()
				elif message.function == '8':
					self.process_reject()
			elif message.file4 == '1':
				self.gcode_gui.new_message(message)
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.context = ''
		text = f'Выберите заказ'
		orders = self.app.order_logic.get_orders_by_type('', self.type)
		orders = self.app.order_logic.get_orders_by_status(orders, 'validate')
		orders = self.app.order_logic.get_orders_by_user_id(orders, self.chat.user_id)
		buttons = self.app.order_logic.convert_orders_to_buttons(orders)
		if buttons:
			buttons.extend(['Назад'])
			self.GUI.tell_buttons(text, buttons, buttons, 1, 0)
		else:
			self.chat.user.designer.first_message(self.message)

	def show_validate(self):
		text = f'Заказ № {self.order.id} "{self.order.name}" \nДата добавления: {self.app.functions.russian_date(self.order.date)}'
		if self.order.quantity > 1:
			text += f'\nКоличество экземпляров: {self.order.quantity}'
		if self.order.quality:
			text += f'\nКачество печати: {self.order.quality}' 
		if self.order.comment:
			text += f'\nКомментарий клиента: {self.order.comment}'

		buttons = [['Принять модель', 'accept'], ['Отказать','reject'], ['Назад']]
		if self.order.model_file:
			self.GUI.tell_document_buttons(self.order.model_file, text, buttons, ['Назад'], 2, self.order.id)
		elif self.order.link:
			self.GUI.tell_link_buttons(self.order.link, text, buttons, buttons, 2, self.order.id)

	def show_accept(self):
		buttons = []
		for type_ in self.app.equipment.printer_types:
			buttons.append([type_.name, type_.id])
		self.GUI.tell_buttons('Выберите тип принтера', buttons, buttons, 3, 0)

	def show_plastic_type(self):
		buttons = []
		for spool in self.app.equipment.spools:
			button = spool.type
			if button not in buttons:
				buttons.append(button)
		text = f'Выберите тип пластика'
		buttons.append(['любой базовый', 'basic'])
		buttons.append(['Подходящего пластика нет', 'unavailable'])
		self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.id)

	def show_weight(self):
		self.chat.set_context(self.address, 5)
		if self.order.quantity > 1:
			text = 'Введите вес одного экземпляра в граммах'
		else:
			text = 'Введите вес стола в граммах'
		self.GUI.tell(text)

	def show_supports(self):
		text = 'Сколько нужно минут на удаление поддержек'
		if self.order.quantity > 1:
			text += ' с одного экземпляра'
		buttons = ['0.5','1','2','3','5','10','15','20']
		buttons.append(['Поддержки не нужны', 'no_supports'])
		self.GUI.tell_buttons(text + '?', buttons, [], 6, self.order.id)

	def show_confirmation(self):
		buttons = ['Подтвердить', 'Отмена']
		self.GUI.tell_buttons('Подтвердите валидацию', buttons, [], 7, self.order.id)

	def show_reject(self):
		self.chat.set_context(self.address, 8)
		self.GUI.tell_buttons('Напишите причину отказа', [['Не уточнять причину', 'none']], [], 8, self.order.id)

	def show_new_order(self, order):
		text = 'Новое задание - валидация '
		if order.type == 'stl':
			text += 'файла'
		elif order.type == 'link':
			text += 'ссылки'
		text += ': ' + order.name
		self.GUI.tell(text)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.chat.user.designer.first_message(self.message)
		else:
			for order in self.app.orders:
				if order.id == int(self.message.btn_data):
					self.order = order
					self.gcode_gui.order = order
					self.show_validate()

	def process_validate(self):
		if self.message.btn_data == 'Назад':
			self.order = None
			self.show_top_menu()
		elif self.message.btn_data == 'accept':
			self.show_accept()
		elif self.message.btn_data == 'reject':
			self.show_reject()

	def process_accept(self):
		for type_ in self.app.equipment.printer_types:
			if type_.id == int(self.message.btn_data):
				self.printer_type = type_.name
		self.show_plastic_type()

	def process_plastic_type(self):
		if self.message.btn_data == 'unavailable':
			user = self.get_user(self.order.user_id)
			user.order_GUI.show_material_unavailable(self.order)
		elif self.message.btn_data == 'basic':
			self.material = 'basic'
		else:
			self.material = self.message.btn_data
		self.show_quantity()

	def process_weight(self):
		self.chat.context = ''
		try:
			self.weight = int(self.message.text)
			self.show_supports()
		except:
			self.show_weight()

	def process_supports(self):
		if self.message.btn_data == 'no_supports':
			self.supports = False
		else:
			self.supports = True
			self.support_minutes = int(self.message.btn_data)
		self.gcode_gui.first_message(self.message)

	def process_gcode_gui(self, gcodes):
		self.gcodes = gcodes
		self.show_confirmation()

	def process_confirmation(self):
		if self.message.btn_data == 'Отмена':
			self.show_validate()
		else:
			for temp_gcode in self.gcodes:
				for i in range(1, temp_gcode.quantity + 1):
					gcode = Gcode(self.app, 0)
					gcode.order_id = self.order.id
					gcode.file_id = temp_gcode.file_id
					gcode.screenshot = temp_gcode.screenshot
					self.app.gcodes_append(gcode)
					self.app.db.create_gcode(gcode)
			self.order.weight = self.weight
			self.order.support_time = self.support_minutes
			self.order.plastic_type = self.material
			self.order.printer_type = self.printer_type
			self.order.price = self.price
			self.order.set_price()
			user = self.get_user(self.order.user_id)
			self.order.logical_status = 'validated'
			user.order_GUI.show_confirmed_by_designer(self.order)
			self.app.db.update_order(self.order)
			self.show_top_menu()

	def process_reject(self):
		self.chat.context = ''
		if self.message.btn_data == 'none':
			reason = ''
		else:
			reason = self.message.text
		# self.order.logical_status = 'rejected'
		user = self.get_user(self.order.user_id)
		user.order_GUI.show_rejected_by_designer(self.order, reason)
		self.app.orders.remove(self.order)
		self.app.db.remove_order(self.order)
		self.order == None
		self.show_top_menu()

#---------------------------- LOGIC ----------------------------

	def get_user(self, user_id):
		for chat in self.app.chats:
			if chat.user_id == user_id:
				return chat.user

	def reset_values(self):
		self.table_weight = 1
		self.supports = False
		self.support_minutes = 0
		self.printer_type = ''
		self.material = ''
		self.price = 0
		self.gcodes = []