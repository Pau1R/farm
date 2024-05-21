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
	colors = None
	color = None

	last_data = ''

	name = ''
	parent = ''
	samplePhoto = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address) 
		self.colors = app.equipment.colors

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
				self.process_sub_colors()
			elif message.function == '5':
				self.process_add_photo()
			elif message.function == '6':
				self.process_edit_photo()
			elif message.function == '7':
				self.process_add_confirmation()
			elif message.function == '8':
				self.process_delete_confirmation()
		if message.type == 'text' or message.type == 'photo':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.colors) > 0:
			text = 'Все цвета:'
		else:
			text = 'Цвета отсутствуют'
		buttons = []
		for color in self.colors:
			if color.parent == '':
				buttons.append([color.name]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_color(self):
		if self.color.parent == '':
			text = f'Цвет: {self.color.name}\n'
		else:
			text = f'Цвет: {self.color.parent}\nОттенок: {self.color.name}\n'
		text += f'Дата добавления: {self.color.date}'
		buttons = ['Поменять картинку']
		if self.color.parent == '':
			no_shades = True
			for color in self.colors:
				if color.parent == self.color.name:
					buttons.append(['Оттенки'])
					no_shades = False
					break
			if no_shades:
				buttons.append('Добавить оттенок')
		buttons.extend(['Удалить', 'Назад'])
		self.GUI.tell_photo_buttons(text, self.color.samplePhoto, buttons, buttons, 2, self.color.name)

	def show_add_new_color(self):
		self.chat.set_context(self.address, 3)
		if self.parent == '':
			text = 'Введите название цвета'
		else:
			text = 'Введите название оттенка'
		self.GUI.tell(text)

	def show_sub_colors(self):
		buttons = []
		for color in self.colors:
			if color.parent == self.color.name:
				buttons.append(color.name)
		buttons.append('Добавить оттенок')
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите оттенок', buttons, buttons, 4, self.color.name)

	def show_add_photo(self):
		self.chat.set_context(self.address, 5)
		self.GUI.tell('Отправьте фото образца')

	def show_edit_photo(self):
		self.chat.set_context(self.address, 6)
		self.GUI.tell('Отправьте фото образца')

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление цвета', buttons, buttons, 7, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Назад']
		self.GUI.tell_buttons('Подтвердите удаление цвета', buttons, buttons, 8, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_color()
		elif self.message.btn_data == 'Назад':
			self.last_data = ''
			self.app.chat.user.admin.show_equipment()
		else:
			for color in self.colors:
				if self.message.btn_data == color.name:
					self.color = color
					self.show_color()

	def process_color(self):
		data = self.message.btn_data
		if data == 'Поменять картинку':
			self.show_edit_photo()
		if data == 'Оттенки':
			self.show_sub_colors()
		if data == 'Добавить оттенок':
			self.parent = self.message.instance_id
			self.show_add_new_color()
		elif data == 'Удалить':
			self.show_delete_confirmation()
		elif data == 'Назад':
			if self.parent == '':
				self.show_top_menu()
			else:
				self.show_sub_colors()

	def process_sub_colors(self):
		data = self.message.btn_data
		if data == 'Добавить оттенок':
			self.show_add_new_color()
		elif data == 'Назад':
			# self.parent = ''
			# for color in self.colors:
			# 	if color.name == self.color.parent:
			# 		self.color = color
			self.show_color()
					# return
			# self.show_top_menu()
		else:
			for color in self.colors:
				if color.name == data and color.parent == self.message.instance_id:
					self.color = color
					self.parent = color.parent
					self.show_color()

	def process_add_new_color(self):
		self.name = self.message.text
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
			self.color = self.app.equipment.create_new_color(self.name, self.parent, self.samplePhoto)
			text = f'Создан новый цвет: {self.color.name}'
			self.GUI.tell_permanent(text)
		self.name = ''
		self.samplePhoto = ''
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.app.db.remove_color(self.color)
			self.colors.remove(self.color)
			if self.parent == '':
				self.show_top_menu()
			else:
				self.show_sub_colors()