import sys
sys.path.append('../lib')
from lib.Gui import Gui

class Gcode_gui:
	last_data = ''
	order = None
	gcode = None
	
	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.order = None
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				x = 1
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				if function == '2':
					self.process_gcode()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		buttons = []
		for gcode in self.app.gcode_logic.get_gcodes(self.order):
			duration = self.app.functions.clean_time(gcode.duration)
			text = f'{gcode.id}: {duration}, статус: {gcode.status}'
			buttons.append([text, gcode.id])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, self.order.id)

	def show_gcode(self):
		gcode = self.gcode
		order = self.app.order_logic.get_order_by_id(gcode.order_id)
		duration = self.app.functions.clean_time(gcode.duration)
		text = f'Заказ: {order.name}\nСтатус: {gcode.status}\nДлительность печати: {duration}\nВес: {gcode.weight} грамм\nЗабронированные катушки:\n'
		for book in gcode.booked:
			text += f'{book[0]}: {book[1]} грамм\n'
		buttons = []
		buttons.append(['Сменить статус','status'])
		buttons.append('Назад')
		self.GUI.tell_photo('', gcode.screenshot)
		self.GUI.tell_document(gcode.file_id, '')
		self.GUI.tell_buttons(text, buttons, buttons, 2, order.id)

	def show_statuses(self):
		text = f'Текущий статус gcode-файла: {self.gcode.status}. Выберите новый статус'
		buttons = []
		# TODO: think over
		# TODO: show list of statuses, taking in account order status

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.chat.user.admin.order_GUI.last_data = ''
			self.chat.user.admin.order_GUI.show_order()
		else:
			self.gcode = self.app.gcode_logic.get_gcode(data)
			self.show_gcode()

	def process_gcode(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_top_menu()
		elif data == 'status':
			self.show_statuses()

	def process_statuses(self):
		# TODO: change status of gcode