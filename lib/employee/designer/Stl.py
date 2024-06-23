import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.order.Order import Order
from lib.Texts import Texts
from lib.order.gcode.Gcode import Gcode

class Stl:
	address = ''

	app = None
	chat = None
	GUI = None
	texts = None
	message = None
	last_data = ''

	order = None
	orders = []
	order_timer = ''

	table_quantity = 1
	table_weight = 1
	supports = False
	support_minutes = 0
	printer_type = ''
	material = ''
	price = 0

	gcode = None
	gcodes = []

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.texts = Texts(chat, address)

	def first_message(self, message):
		self.table_quantity = 1
		self.table_weight = 1
		self.supports = False
		self.support_minutes = 0
		self.printer_type = ''
		self.material = ''
		self.price = 0
		self.gcodes = []
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
			elif message.function == '2':
				self.process_validate()
			elif message.function == '3':
				self.process_accept()
			elif message.function == '4':
				self.process_plastic_type()
			elif message.function == '5':
				self.process_quantity()
			elif message.function == '6':
				self.process_weight()
			elif message.function == '7':
				self.process_supports()
			elif message.function == '8':
				self.process_supports_time()
			elif message.function == '9':
				self.process_gcode()
			elif message.function == '10':
				self.process_gcode_screenshot()
			elif message.function == '11':
				self.process_gcode_quantity()
			elif message.function == '12':
				self.process_gcode_hours()
			elif message.function == '13':
				self.process_gcode_minutes()
			elif message.function == '14':
				self.process_confirmation()
			elif message.function == '15':
				self.process_reject()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.context = ''
		text = f'Выберите модель для валидации'
		if self.app.orders == []:
			text = 'Модели отсутствуют'
		buttons = self.app.order_logic.get_orders_for_validation_buttons(self.chat.user_id, 'stl')
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

	def show_quantity(self):
		if self.order.quantity > 1:
			buttons = []
			for i in range(1, self.order.quantity + 1):
				buttons.append(str(i))
			self.GUI.tell_buttons('Выберите кол-во моделей на одном столе', buttons, [], 5, self.order.id)
		else:
			self.show_weight()

	def show_weight(self):
		self.chat.set_context(self.address, 6)
		self.GUI.tell('Введите вес стола в граммах')

	def show_supports(self):
		self.GUI.tell_buttons('Нужно ли печатать поддержки?', ['Да','Нет'], [], 7, self.order.id)

	def show_supports_time(self):
		text = 'Сколько нужно минут на удаление поддержек'
		if self.order.quantity > 1:
			text += ' с одного экземпляра'
		self.GUI.tell_buttons(text + '?', ['0.5','1','2','3','5','10','15','20'], [], 8, self.order.id)

	def show_gcode(self):
		self.chat.set_context(self.address, 9)
		text = 'Загрузите файл gcode'
		if self.gcodes:
			buttons = [['Загрузку закончил', 'uploaded']]
			self.GUI.tell_buttons(text, buttons, [], 9, self.order.id)
		else:
			self.GUI.tell(text)

	def show_gcode_screenshot(self):
		self.chat.set_context(self.address, 10)
		text = 'Сделайте скриншот в слайсере gcode файла и загрузите его'
		self.GUI.tell(text)

	def show_gcode_quantity(self):
		self.chat.set_context(self.address, 11)
		text = 'Выберите либо введите кол-во экземпляров загруженного файла'
		buttons = ['1','2','3','4','5','6','7','8','9','10']
		self.GUI.tell_buttons(text, buttons, [], 11, self.order.id)

	def show_gcode_hours(self):
		text = 'Выберите длительность печати файла (часы):'
		buttons = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
		self.GUI.tell_buttons(text, buttons, [], 12, self.order.id)

	def show_gcode_minutes(self):
		text = 'Выберите длительность печати файла (минуты):'
		buttons = ['5','10','15','20','25','30','35','40','45','50','55']
		self.GUI.tell_buttons(text, buttons, [], 13, self.order.id)

	def show_confirmation(self):
		buttons = ['Подтвердить', 'Отмена']
		self.GUI.tell_buttons('Подтвердите валидацию', buttons, [], 14, self.order.id)

	def show_reject(self):
		self.chat.set_context(self.address, 15)
		self.GUI.tell_buttons('Напишите причину отказа', [['Не уточнять причину', 'none']], [], 15, self.order.id)

	def show_new_order(self, order):
		self.GUI.tell('Поступил новый заказ на валидацию файла модели: ' + order.name)

	# def show_finished_orders(self):
	# 	buttons = []
	# 	buttons.extend(['Назад'])
	# 	self.GUI.tell_buttons('', buttons, ['Назад'], )

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.chat.user.designer.first_message(self.message)
		else:
			for order in self.app.orders:
				if order.id == int(self.message.btn_data):
					self.order = order
					self.show_validate()

	def process_validate(self):
		if self.message.btn_data == 'Назад':
			self.order = None
			self.show_top_menu()
		elif self.message.btn_data == 'accept':
			if self.app.testing:
				self.process_confirmation()
			else:
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

	def process_quantity(self):
		try:
			self.table_quantity = int(self.message.btn_data)
			self.show_weight()
		except:
			self.show_quantity()

	def process_weight(self):
		self.chat.context = ''
		try:
			self.table_weight = int(self.message.text)
			self.show_supports()
		except:
			self.show_weight()

	def process_supports(self):
		if self.message.btn_data == 'Да':
			self.supports = True
			self.show_supports_time()
		else:
			self.supports = False
			self.show_gcode()

	def process_supports_time(self):
		try:
			self.support_minutes = int(self.message.btn_data)
		except:
			self.show_supports_time()
			return
		self.show_gcode()

	def process_gcode(self):
		self.chat.context = ''
		if self.message.btn_data == 'uploaded':
			self.show_confirmation()
		else:
			file_id = self.message.file_id
			if self.message.type in ['document'] and file_id and self.message.file_name.split(".")[-1] == 'gcode':
				self.gcode = Gcode(self.app, 0)
				self.gcodes.append(self.gcode)
				self.gcode.file_id = file_id
				self.show_gcode_screenshot()
			else:
				self.show_gcode()

	def process_gcode_screenshot(self):
		self.chat.context = ''
		file_id = self.message.file_id
		if self.message.type in ['photo'] and file_id:
			self.gcode.screanshot = file_id
			self.show_gcode_quantity()
		else:
			self.show_gcode_screenshot()

	def process_gcode_quantity(self):
		self.chat.context = ''
		try:
			if self.message.btn_data:
				quantity = self.message.btn_data
			else:
				quantity = self.message.text
			self.gcode.quantity = int(quantity)
			self.show_gcode_hours()
		except:
			self.show_gcode_quantity()

	def process_gcode_hours(self):
		try:
			hours = int(self.message.btn_data)
			self.gcode.duration = hours * 60
			self.show_gcode_minutes()
		except:
			self.show_gcode_hours()

	def process_gcode_minutes(self):
		try:
			minutes = int(self.message.btn_data)
			self.gcode.duration += minutes
			self.show_gcode()
		except:
			self.show_gcode_minutes()

	def process_confirmation(self):
		if self.app.testing:
			self.table_weight = 200
			self.table_quantity = 3
			self.support_minutes = 1
			self.material = 'basic'
			self.printer_type = 'Bambu lab P1S'
			gcode_ = Gcode(self.app, 0)
			gcode_.quantity = 1
			gcode_.duration = 200
			gcode_.file_id = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'
			self.gcodes.append(gcode_)
			self.screanshot = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'

		if self.message.btn_data == 'Отмена':
			self.show_validate()
		else:
			for temp_gcode in self.gcodes:
				for i in range(1, temp_gcode.quantity + 1):
					gcode = Gcode(self.app, 0)
					gcode.order_id = self.order.id
					gcode.file_id = temp_gcode.file_id
					gcode.screanshot = temp_gcode.screanshot
					self.app.gcodes_append(gcode)
					self.app.db.create_gcode(gcode)
			self.order.weight = self.table_weight / self.table_quantity
			self.order.support_time = self.support_minutes
			self.order.plastic_type = self.material
			self.order.printer_type = self.printer_type
			self.order.price = self.price
			self.order.set_price()
			user = self.get_user(self.order.user_id)
			if not self.app.testing:
				self.order.logical_status = 'validated'
			user.order_GUI.show_confirmed_by_designer(self.order)
			self.app.db.update_order(self.order)
			self.show_top_menu()

	def process_reject(self):
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