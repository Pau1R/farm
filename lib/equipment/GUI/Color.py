import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.Texts import Texts
from datetime import date

class ColorGUI:
	address = '1/2/7'

	app = None
	chat = None
	GUI = None
	texts = None
	color = None

	last_data = ''

	name = ''
	shade = ''
	samplePhoto = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address) 

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
			elif message.function == '2':
				self.process_color()
			elif message.function == '3':
				self.process_add_new_color()
			elif message.function == '4':
				self.process_add_new_shade()
			elif message.function == '5':
				self.process_add_photo()
			elif message.function == '6':
				self.process_edit_photo()
			elif message.function == '7':
				self.process_add_confirmation()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.colors) > 0:
			text = 'Все цвета:'
		else:
			text = 'Цвета отсутствуют'
		buttons = []
		for color in self.app.equipment.colors:
			buttons.append([color.name]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_color(self):
		text = f'Цвет: {self.color.name}\nДата добавления: {self.color.date}'
		buttons = ['Поменять картинку']
		buttons.extend(['Удалить', 'Назад'])
		self.GUI.tell_photo_buttons(text, self.color.samplePhoto, buttons, buttons, 2, 0)

	def show_add_new_color(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Введите название цвета (в следующем запросе - оттенок)')

	def show_add_new_shade(self):
		self.chat.set_context(self.address, 4)
		self.GUI.tell_buttons('Введите название отенка', ['Оттенка нет'], [], 4, 0)

	def show_add_photo(self):
		self.chat.set_context(self.address, 5)
		self.GUI.tell('Отправьте фото образца')

	def show_edit_photo(self):
		self.chat.set_context(self.address, 6)
		self.GUI.tell('Отправьте фото образца')

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление цвета', buttons, ['Подтверждаю', 'Отменить добавление'], 7, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_color()
		elif self.message.btn_data == 'Назад':
			self.last_data = ''
			self.app.chat.user.admin.show_equipment()
		else:
			for color in self.app.equipment.colors:
				if self.message.btn_data == color.name:
					self.color = color
					self.show_color()

	def process_color(self):
		if self.message.btn_data == 'Поменять картинку':
			self.show_edit_photo()
		elif self.message.btn_data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_new_color(self):
		self.name = self.message.text
		self.show_add_new_shade()
	
	def process_add_new_shade(self):
		if not self.message.btn_data == 'Оттенка нет':
			self.shade = self.message.text
		self.show_add_photo()

	def process_add_photo(self):
		if self.message.type == 'photo':
			self.samplePhoto = self.message.file_id
			self.show_add_confirmation()
		else:
			self.show_add_photo()

	def process_edit_photo(self):
		if self.message.type == 'photo':
			self.color.samplePhoto = self.message.file_id
			self.show_color()
		else:
			self.show_edit_photo()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.color = self.app.equipment.create_new_color(self.name, self.shade, self.samplePhoto)
			text = f'Создан новый цвет: {self.color.name}'
			self.GUI.tell_permanent(text)
		self.name = ''
		self.samplePhoto = ''
		self.show_top_menu()