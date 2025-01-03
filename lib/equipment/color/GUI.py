import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui
from datetime import date
import time

class ColorGUI:
	last_data = ''

	name = ''
	parent_id = 0
	samplePhoto = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.colors = app.equipment.colors
		self.color = None

	def first_message(self, message):
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
					self.process_color()
				elif function == '3':
					self.process_add_new_color()
				elif function == '4':
					self.process_sub_colors()
				elif function == '5':
					self.process_add_photo()
				elif function == '6':
					self.process_edit_photo()
				elif function == '7':
					self.process_add_confirmation()
				elif function == '8':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.colors) > 0:
			text = 'Все цвета:'
		else:
			text = 'Цвета отсутствуют'
		buttons = []
		for color in self.colors:
			if color.parent_id == 0:
				buttons.append([color.name, color.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_color(self):
		if self.color.parent_id == 0:
			text = 'Цвет'
		else:
			text = f'Оттенок'
		text += f': {self.color.name}\nДата добавления: {self.color.created}'
		buttons = ['Поменять картинку']
		if self.color.parent_id == 0:
			no_shades = True
			for color in self.colors:
				if color.parent_id == self.color.id:
					buttons.append('Оттенки')
					no_shades = False
					break
			if no_shades:
				buttons.append('Добавить оттенок')
		buttons.extend(['Удалить', 'Назад'])
		self.GUI.tell_photo_buttons(text, self.color.samplePhoto, buttons, buttons, 2, self.color.id)

	def show_add_new_color(self):
		self.chat.set_context(self.address, 3)
		if self.parent_id == 0:
			text = 'Введите название цвета'
		else:
			text = 'Введите название оттенка'
		self.GUI.tell(text)

	def show_sub_colors(self):
		if self.color.parent_id != 0:
			for color in self.colors:
				if color.id == self.color.parent_id:
					self.color = color
		buttons = []
		for color in self.colors:
			if color.parent_id == self.color.id:
				buttons.append([color.name, color.id])
		if buttons == []:
			self.show_color()
		buttons.append('Добавить оттенок')
		buttons.append('Назад')
		self.GUI.tell_buttons(f'Оттенки цвета {self.color.name}:', buttons, buttons, 4, self.color.id)

	def show_add_photo(self):
		self.chat.set_context(self.address, 5)
		self.GUI.tell('Отправьте фото образца')

	def show_edit_photo(self):
		self.chat.set_context(self.address, 6)
		self.GUI.tell('Отправьте фото образца')

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		if self.parent_id == 0:
			text = 'цвета'
		else:
			text = 'оттенка'
		self.GUI.tell_buttons('Подтвердите добавление ' + text, buttons, buttons, 7, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Назад']
		if self.parent_id == 0:
			text = 'цвета'
		else:
			text = 'оттенка'
		self.GUI.tell_buttons('Подтвердите удаление ' + text, buttons, buttons, 8, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_color()
		elif self.message.btn_data == 'Назад':
			self.last_data = ''
			self.app.chat.user.admin.show_equipment()
		else:
			for color in self.colors:
				if color.id == int(self.message.btn_data):
					self.color = color
					self.show_color()

	def process_color(self):
		data = self.message.btn_data
		if data == 'Поменять картинку':
			self.show_edit_photo()
		if data == 'Оттенки':
			self.parent_id = self.color.id
			self.show_sub_colors()
		if data == 'Добавить оттенок':
			self.parent_id = int(self.message.instance_id)
			self.show_add_new_color()
		elif data == 'Удалить':
			count = self.busy_colors()
			if count == 0:
				self.show_delete_confirmation()
			else:
				self.GUI.tell(f'Нельзя удалить этот цвет, он назначен {count} катушкам')
				time.sleep(3)
				self.show_color()
		elif data == 'Назад':
			if self.parent_id == 0:
				self.show_top_menu()
			else:
				self.show_sub_colors()

	def process_sub_colors(self):
		data = self.message.btn_data
		if data == 'Добавить оттенок':
			self.show_add_new_color()
		elif data == 'Назад':
			for color in self.colors:
				if color.id == self.parent_id:
					self.color = color
			self.parent_id = 0
			self.show_color()
		else:
			for color in self.colors:
				if color.id == int(data) and color.parent_id == int(self.message.instance_id):
					self.color = color
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
			self.color = self.app.equipment.create_new_color(self.name, self.parent_id, self.samplePhoto)
			if self.parent_id == 0:
				text = f'цвет: {self.color.name}'
			else:
				text = f'оттенок: {self.color.name}'
			self.GUI.tell_permanent('Создан новый ' + text)
		self.name = ''
		self.samplePhoto = ''
		if self.parent_id == 0:
			self.show_top_menu()
		else:
			self.show_sub_colors()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.app.db.remove_color(self.color)
			self.colors.remove(self.color)
			if self.parent_id == 0:
				self.show_top_menu()
			else:
				self.show_sub_colors()
		else:
			self.show_color()

#---------------------------- PROCESS ----------------------------

	def busy_colors(self):
		count = 0
		for spool in self.app.equipment.spools:
			if spool.color_id == self.color.id:
				count += 1
		return count