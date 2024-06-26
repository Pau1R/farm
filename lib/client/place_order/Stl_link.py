import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.client.place_order.GUI.General import General_parameters

class Stl_link:
	address = ''

	app = None
	chat = None
	order = None
	GUI = None

	general_parameters = None

	supported_files = ['stl', 'obj', 'step', 'svg', '3mf', 'amf']

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.general_parameters = General_parameters(app, chat, address + '/1')

	def first_message(self, message):
		self.order = self.chat.user.order
		self.order.sketches = []
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format:
			if message.file3 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.process_top_menu()
			elif message.file3 == '1':
				self.general_parameters.new_message(message)
		if message.type in ['text', 'document', 'photo']:
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.set_context(self.address, 1)
		if self.order.type == 'stl':
			text = 'Загрузите свой 3д файл. Поддерживаются следующие форматы: ' + ', '.join(self.supported_files)
		elif self.order.type == 'link':
			text = 'Отправьте ссылку на модель из интернета'
		self.GUI.tell(text)

	def show_extention_error(self):
		self.GUI.tell('Неверный формат файла')
		self.show_top_menu()

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.chat.context = ''
		if self.order.type == 'stl':
			if self.message.type == 'document' and self.message.file_name.split(".")[-1] in self.supported_files:
				self.order.model_file = self.message.file_id
				self.general_parameters.first_message(self.message)
			else:
				self.show_extention_error()
		elif self.order.type == 'link' and self.message.type == 'text':
			self.order.link = self.message.text
			self.general_parameters.first_message(self.message)
