import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.order.gcode.Gcode import Gcode

class Gcode_gui:
	last_data = ''

	def __init__(self, app, chat, address, parent):
		self.app = app
		self.chat = chat
		self.order = None
		self.message = None
		self.address = address
		self.parent = parent
		self.GUI = Gui(app, chat, address)
		self.gcode = None
		self.gcodes = []

	def first_message(self, message):
		self.gcodes = []
		self.last_data = ''
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
					self.process_screenshot()
				elif function == '3':
					self.process_weight()
				elif function == '4':
					self.process_hours()
				elif function == '5':
					self.process_minutes()
				elif function == '6':
					self.process_quantity()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.set_context(self.address, 1)
		text = 'Загрузка информации из слайсера\n\n1) Загрузите файл gcode'
		if self.gcodes:
			text += f'\n\nфайлов загружено: {len(self.gcodes)}'
			buttons = [['Загрузку закончил', 'uploaded']]
			self.GUI.tell_buttons(text, buttons, [], 1, self.order.id)
		else:
			self.GUI.tell(text)

	def show_screenshot(self):
		self.chat.set_context(self.address, 2)
		text = 'Загрузка информации из слайсера\n\n2) Загрузите скриншот'
		self.GUI.tell(text)

	def show_weight(self):
		self.chat.set_context(self.address, 3)
		text = 'Загрузка информации из слайсера\n\n3) Введите вес'
		self.GUI.tell(text)

	def show_hours(self):
		text = 'Загрузка информации из слайсера\n\n4.1) Выберите длительность печати файла (часы):'
		buttons = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
		self.GUI.tell_buttons(text, buttons, [], 4, self.order.id)

	def show_minutes(self):
		text = 'Загрузка информации из слайсера\n\n4.2) Выберите длительность печати файла (минуты):'
		buttons = ['0','5','10','15','20','25','30','35','40','45','50','55']
		self.GUI.tell_buttons(text, buttons, [], 5, self.order.id)

	def show_quantity(self):
		self.chat.set_context(self.address, 6)
		text = 'Выберите либо введите сколько раз печатать загруженный файл'
		buttons = ['1','2','3','4','5','6','7','8','9','10']
		self.GUI.tell_buttons(text, buttons, [], 6, self.order.id)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.chat.context = ''
		if self.message.btn_data == 'uploaded':
			self.parent.last_data = ''
			self.parent.process_gcode_gui(self.gcodes)
		else:
			file_id = self.message.file_id
			if self.message.type in ['document'] and file_id and self.message.file_name.split(".")[-1] == 'gcode':
				self.gcode = Gcode(self.app, 0)
				self.gcodes.append(self.gcode)
				self.gcode.file_id = file_id
				self.show_screenshot()
			else:
				self.show_top_menu()

	def process_screenshot(self):
		self.chat.context = ''
		file_id = self.message.file_id
		if self.message.type in ['photo'] and file_id:
			self.gcode.screenshot = file_id
			self.show_weight()
		else:
			self.show_screenshot()

	def process_weight(self):
		self.chat.context = ''
		try:
			self.gcode.weight = int(self.message.text)
		except:
			self.show_weight()
			return
		self.show_hours()

	def process_hours(self):
		try:
			hours = int(self.message.btn_data)
			self.gcode.duration = hours * 60
		except:
			self.show_hours()
			return
		self.show_minutes()

	def process_minutes(self):
		try:
			minutes = int(self.message.btn_data)
			self.gcode.duration += minutes
			if self.order.quantity == 1:
				self.show_top_menu()
			else:
				self.show_quantity()
		except:
			self.show_minutes()

	def process_quantity(self):
		self.chat.context = ''
		try:
			if self.message.btn_data:
				quantity = self.message.btn_data
			else:
				quantity = self.message.text
			self.gcode.quantity = int(quantity)
			self.show_top_menu()
		except:
			self.show_quantity()