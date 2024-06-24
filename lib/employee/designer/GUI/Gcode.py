import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.order.gcode.Gcode import Gcode

class Gcode_gui:
	address = ''

	app = None
	chat = None
	parent = None
	GUI = None
	message = None
	last_data = ''
	order = None

	gcode = None
	gcodes = []

	def __init__(self, app, chat, address, parent):
		self.app = app
		self.chat = chat
		self.address = address
		self.parent = parent
		self.GUI = Gui(app, chat, address)

	def first_message(self, message):
		self.gcodes = []
		self.last_data = ''
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
			elif message.function == '2':
				self.process_gcode_screenshot()
			elif message.function == '3':
				self.process_gcode_quantity()
			elif message.function == '4':
				self.process_gcode_hours()
			elif message.function == '5':
				self.process_gcode_minutes()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.set_context(self.address, 1)
		text = 'Загрузите файл gcode'
		if self.gcodes:
			buttons = [['Загрузку закончил', 'uploaded']]
			self.GUI.tell_buttons(text, buttons, [], 1, self.order.id)
		else:
			self.GUI.tell(text)

	def show_gcode_screenshot(self):
		self.chat.set_context(self.address, 2)
		text = 'Сделайте скриншот в слайсере gcode файла и загрузите его'
		self.GUI.tell(text)

	def show_gcode_quantity(self):
		self.chat.set_context(self.address, 3)
		text = 'Выберите либо введите кол-во экземпляров загруженного файла'
		buttons = ['1','2','3','4','5','6','7','8','9','10']
		self.GUI.tell_buttons(text, buttons, [], 3, self.order.id)

	def show_gcode_hours(self):
		text = 'Выберите длительность печати файла (часы):'
		buttons = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
		self.GUI.tell_buttons(text, buttons, [], 4, self.order.id)

	def show_gcode_minutes(self):
		text = 'Выберите длительность печати файла (минуты):'
		buttons = ['5','10','15','20','25','30','35','40','45','50','55']
		self.GUI.tell_buttons(text, buttons, [], 5, self.order.id)

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
				self.show_gcode_screenshot()
			else:
				self.show_top_menu()

	def process_gcode_screenshot(self):
		self.chat.context = ''
		file_id = self.message.file_id
		if self.message.type in ['photo'] and file_id:
			self.gcode.screenshot = file_id
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
			self.show_top_menu()
		except:
			self.show_gcode_minutes()