import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.order.Order import Order
from lib.order.GUI import Order_GUI
from lib.order.gcode.Gcode import Gcode
from lib.employee.designer.GUI.Gcode import Gcode_gui

class General:
	type = ''
	status = ''
	
	last_data = ''

	order_timer = ''

	weight = 1
	supports = False
	support_minutes = 0
	printer_type = ''
	material = ''
	price = 0

	design_time = 0
	print_time = 0

	gcode_gui = None
	gcodes = []

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.order = None
		self.message = None
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.gcode_gui = Gcode_gui(app, chat, address + '/1', self)
		self.order_GUI = Order_GUI(app, chat, address + '/2')

	def first_message(self, message, type_, status):
		self.reset_values()
		self.type = type_
		self.status = status
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				self.gcode_gui.new_message(message)
			elif file == '2':
				self.order_GUI.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				# elif function == '2':
				# 	self.process_order()
				elif function == '3':
					self.process_design_time()
				elif function == '4':
					self.process_print_time()
				elif function == '5':
					self.process_weight()
				elif function == '6':
					self.process_printer_type()
				elif function == '7':
					self.process_plastic_type()
				elif function == '8':
					self.process_supports()
				elif function == '9':
					self.process_confirmation()
				elif function == '10':
					self.process_reject()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.context = ''
		text = f'Выберите заказ'
		logic = self.app.order_logic
		orders = logic.get_orders_by_type(self.app.orders, self.type)
		orders = logic.get_orders_by_status(orders, self.status)
		orders = logic.get_orders_by_user_id(orders, self.chat.user_id)
		buttons = logic.convert_orders_to_buttons(orders)
		if buttons:
			buttons.extend(['Назад'])
			self.GUI.tell_buttons(text, buttons, buttons, 1, 0)
		else:
			self.chat.user.designer.first_message(self.message)

	def show_order(self):
		self.message.instance_id = self.message.btn_data
		self.order_GUI.last_data = ''
		self.order_GUI.first_message(self.message)

	def show_design_time(self):
		text = 'Сколько часов ушло на разработку модели и слайсинг?'
		if self.order.logical_status == 'prevalidate':
			text = 'Примерно сколько часов нужно на разработку модели и слайсинг?'
		buttons = ['0.25','0.5','0.75','1','1.5','2','2.5','3','3.5','4','4.5','5','5.5','6','6.5','7','7.5','8','9','10']
		self.GUI.tell_buttons(text, buttons, [], 3, self.order.id)

	def show_print_time(self):
		text = 'Примерно сколько времено нужно на печать (с запасом)'
		if self.order.quantity > 1:
			text += ' одного экземпляра?'
		else:
			text += '?'
		buttons = ['0.5','1','1.5','2','2.5','3','4','5','6','7','9','11','13','16','19','22','26','30','35','40','50','70','100']
		self.GUI.tell_buttons(text, buttons, [], 4, self.order.id)

	def show_weight(self):
		self.chat.set_context(self.address, 5)
		text = 'Введите вес'
		if self.order.logical_status == 'prevalidate':
			text = 'Введите примерный вес (с хорошим запасом)'
		if self.order.quantity > 1:
			text += ' одного экземпляра в граммах'
		else:
			text += ' в граммах'
		self.GUI.tell(text)

	def show_printer_type(self):
		buttons = []
		for type_ in self.app.equipment.printer_types:
			buttons.append([type_.name, type_.id])
		buttons.append(['Любой','*'])
		self.GUI.tell_buttons('Выберите тип принтера', buttons, buttons, 6, self.order.id)

	def show_plastic_type(self):
		buttons = []
		for spool in self.app.equipment.spools:
			button = spool.type
			if button not in buttons:
				buttons.append(button)
		text = f'Выберите тип пластика'
		buttons.append(['любой базовый', 'basic'])
		buttons.append(['Подходящего пластика нет', 'unavailable'])
		self.GUI.tell_buttons(text, buttons, buttons, 7, self.order.id)

	def show_supports(self):
		text = 'Сколько нужно минут на удаление поддержек'
		if self.order.logical_status == 'prevalidate':
			text = 'Примерно сколько нужно минут на удаление поддержек'
		if self.order.quantity > 1:
			text += ' с одного экземпляра'
		buttons = ['1','2','3','5','10','15','20']
		buttons.append(['Поддержки не нужны', 'no_supports'])
		self.GUI.tell_buttons(text + '?', buttons, [['Поддержки не нужны', 'no_supports']], 8, self.order.id)

	def show_confirmation(self):
		buttons = ['Подтвердить', 'Отмена']
		self.GUI.tell_buttons('Подтвердите валидацию', buttons, [], 9, self.order.id)

	# def show_reject(self):
	# 	self.chat.set_context(self.address, 10)
	# 	self.GUI.tell_buttons('Напишите причину отказа', [['Не уточнять причину', 'none'], 'Назад'], [], 10, self.order.id)

	# sketch and item:

	# реакция клиента:
	# - выбор цвета, бронь пластика и предоплата
	
	# разработка модели

	# внесение конкретизированных данных (стандартная валидация)

	def show_new_order(self, order):
		text = 'Новое задание - валидация '
		if order.type == 'stl':
			text += 'файла'
		elif order.type == 'link':
			text += 'ссылки'
		elif order.type == 'sketch':
			text += 'чертежа'
		elif order.type == 'item':
			text += 'предмета по фотографиям'
		elif order.type == 'production':
			text += 'мелкосерийного заказа'
		text += f': {order.name} (№ {order.id})'
		self.GUI.tell(text)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.chat.user.designer.last_data = ''
			self.chat.user.designer.first_message(self.message)
		else:
			for order in self.app.orders:
				if order.id == int(self.message.btn_data):
					self.order = order
					self.gcode_gui.order = order
					self.show_order()

	def order_accepted(self, data):
		if self.order.type in ['sketch','item']:
			self.show_design_time()
		else:
			self.show_printer_type()

	def process_design_time(self):
		try:
			self.design_time = int(float(self.message.btn_data) * 60)
			self.show_printer_type()
			if self.order.logical_status == 'prevalidate':
				self.show_print_time()
			else:
				self.show_printer_type()
		except:
			self.show_design_time()

	def process_print_time(self):
		try:
			self.print_time = int(float(self.message.btn_data) * 60)
			self.show_weight()
		except:
			self.show_print_time()

	def process_weight(self):
		self.chat.context = ''
		try:
			self.weight = int(self.message.text)
			self.show_printer_type()
		except:
			self.show_weight()

	def process_printer_type(self):
		data = self.message.btn_data
		if data == '*':
			self.printer_type = '*'
		else:
			self.printer_type = int(data)
		self.show_plastic_type()

	def process_plastic_type(self):
		if self.message.btn_data == 'unavailable':
			user = self.get_user(self.order.user_id)
			user.order_GUI.show_material_unavailable(self.order)
		elif self.message.btn_data == 'basic':
			self.material = 'basic'
		else:
			self.material = self.message.btn_data
		self.show_supports()

	def process_supports(self):
		if self.message.btn_data == 'no_supports':
			self.supports = False
		else:
			self.supports = True
			self.support_minutes = int(self.message.btn_data)
		if self.order.logical_status == 'prevalidate':
			self.show_confirmation()
		else:
			self.gcode_gui.first_message(self.message)

	def process_gcode_gui(self, gcodes):
		self.gcodes = gcodes
		self.show_confirmation()

	def process_confirmation(self):
		order = self.order
		if self.message.btn_data == 'Отмена':
			self.show_order()
		else:
			for temp_gcode in self.gcodes:
				for i in range(1, temp_gcode.quantity + 1):
					self.print_time = 0
					gcode = Gcode(self.app, 0)
					gcode.order_id = order.id
					gcode.file_id = temp_gcode.file_id
					gcode.screenshot = temp_gcode.screenshot
					self.app.gcodes_append(gcode)
					self.app.db.create_gcode(gcode)
			if order.booked:
				statuses = ['stock']
				if 'ordered' not in statuses:
					for book in order.booked:
						spool = self.app.equipment.spool_logic.get_spool(book[0])
						if spool.status == 'ordered':
							statuses.append('ordered')
				order.reserve_plastic(statuses, order.color_id)
			order.design_time = self.design_time
			order.print_time = self.print_time
			order.weight = self.weight
			order.support_time = self.support_minutes
			order.plastic_type = self.material
			order.printer_type = self.printer_type
			order.set_price()
			user = self.get_user(order.user_id)
			order.logical_status = 'validated'
			user.order_GUI.show_confirmed_by_designer(order)
			self.app.db.update_order(order)
			self.show_top_menu()

	def process_reject(self):
		self.chat.context = ''
		data = self.message.btn_data
		if data == 'Назад':
			self.show_order()
			return
		elif data == 'none':
			reason = ''
		else:
			reason = self.message.text
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
		self.design_time = 0
		self.print_time = 0