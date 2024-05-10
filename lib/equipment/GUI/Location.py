import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class LocationGUI:
	app = None
	chat = None
	GUI = None
	location = None

	name = ''
	type = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat)

	def first_message(self, message):
		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.messages_append(message)
		# self.GUI.messages.append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_top_menu()
		elif context == 'top_menu':
			self.process_top_menu()

		elif context == 'location':
			self.process_location()

		elif context == 'add_new_location':
			self.process_add_new_location()
		elif context == 'add_new_location_type':
			self.process_add_new_location_type()
		elif context == 'add_confirmation':
			self.process_add_confirmation()
		elif context == 'delete_confirmation':
			self.process_delete_confirmation()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		if len(self.app.equipment.locations) > 0:
			text = 'Все локации:'
		else:
			text = 'Локации отсутствуют'
		buttons = []
		for location in self.app.equipment.locations:
			buttons.append([f'{location.id}: {location.type} {location.name}', location.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'])

	def show_location(self):
		self.context = 'location'
		text = f'номер локации: {self.location.id}\nдата добавления: {self.location.date}\n'
		text += f'название: {self.location.name}\nтип: {self.location.type}\n'
		buttons = []
		buttons.extend(['Удалить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Удалить', 'Назад'])

	def show_add_new_location(self):
		self.context = 'add_new_location'
		self.GUI.tell('Введите название локации')

	def show_add_new_location_type(self):
		self.context = 'add_new_location_type'
		buttons = []
		buttons.extend(['Помещение', 'Зона'])
		self.GUI.tell_buttons('Выберите тип локации:', buttons, [])

	def show_add_confirmation(self):
		self.context = 'add_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить добавление')
		self.GUI.tell_buttons('Подтвердите добавление локации', buttons, ['Подтверждаю', 'Отменить добавление'])

	def show_delete_confirmation(self):
		self.context = 'delete_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить удаление')
		self.GUI.tell_buttons('Подтвердите удаление локации', buttons, ['Подтверждаю', 'Отменить удаление'])

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Добавить':
			self.show_add_new_location()
		elif self.message.data == 'Назад':
			self.app.chat.user.employee.show_equipment()
		else:
			for location in self.app.equipment.locations:
				if self.message.data == location.id:
					self.location = location
					self.show_location()

	def process_location(self):
		self.context = ''
		if self.message.data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.data == 'Назад':
			self.show_top_menu()

	def process_add_new_location(self):
		self.context = ''
		self.name = self.message.text
		self.show_add_new_location_type()

	def process_add_new_location_type(self):
		self.context = ''
		self.type = self.message.data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.location = self.app.equipment.create_new_location(self.name, self.type)
			text = f'Создана новая локация:\nномер: {self.location.id}\nназвание: {self.location.name}\n'
			text += f'тип: {self.location.type}'
			self.GUI.tell(text)
		self.name = ''
		self.type = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.GUI.tell(f'Локация {self.location.id} удалена')
			self.app.equipment.remove_location(self.location.id)
			self.location = None
		self.show_top_menu()