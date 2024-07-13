import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class LocationGUI:
	last_data = ''

	name = ''
	type = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.location = None

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
					self.process_location()
				elif function == '3':
					self.process_add_new_location()
				elif function == '4':
					self.process_add_new_location_type()
				elif function == '5':
					self.process_add_confirmation()
				elif function == '6':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.locations) > 0:
			text = 'Все локации:'
		else:
			text = 'Локации отсутствуют'
		buttons = []
		for location in self.app.equipment.locations:
			buttons.append([f'{location.id}: {location.type} {location.name}', location.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_location(self):
		text = f'номер локации: {self.location.id}\nдата добавления: {self.location.created}\n'
		text += f'название: {self.location.name}\nтип: {self.location.type}\n'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_add_new_location(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Введите название локации')

	def show_add_new_location_type(self):
		buttons = ['Помещение', 'Зона']
		self.GUI.tell_buttons('Выберите тип локации:', buttons, [], 4, 0)

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление локации', buttons, buttons, 5, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление локации', buttons, buttons, 6, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_location()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for location in self.app.equipment.locations:
				if location.id == int(self.message.btn_data):
					self.location = location
					self.show_location()

	def process_location(self):
		if self.message.btn_data == 'Удалить':
			# TODO: refuse if anything is in location
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_new_location(self):
		self.name = self.message.text
		self.show_add_new_location_type()

	def process_add_new_location_type(self):
		self.type = self.message.btn_data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.location = self.app.equipment.create_new_location(self.name, self.type)
			text = f'Создана новая локация:\nномер: {self.location.id}\nназвание: {self.location.name}\n'
			text += f'тип: {self.location.type}'
			self.GUI.tell_permanent(text)
		self.name = ''
		self.type = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Локация {self.location.id} удалена')
			self.app.equipment.remove_location(self.location.id)
			self.location = None
		self.show_top_menu()