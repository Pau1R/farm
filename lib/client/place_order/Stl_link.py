import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.client.place_order.GUI.General import General_parameters

class Stl_link:
	supported_files = ['stl', 'obj', 'step', 'svg', '3mf', 'amf']

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.order = None
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

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				self.general_parameters.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
		self.chat.add_if_text(self)

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
