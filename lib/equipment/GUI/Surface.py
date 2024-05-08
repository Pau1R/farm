import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.Texts import Texts

class SurfaceGUI:
	app = None
	chat = None
	GUI = None
	surface = None
	texts = Texts()

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
		self.GUI.messages.append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_top_menu()
		elif context == 'top_menu':
			self.process_top_menu()

		elif context == 'surface':
			self.process_surface()

		elif context == 'add_new_surface':
			self.process_add_new_surface()
		elif context == 'add_confirmation':
			self.process_add_confirmation()
		elif context == 'delete_confirmation':
			self.process_delete_confirmation()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		if len(self.app.equipment.surfaces) > 0:
			text = 'Все поверхности:'
		else:
			text = 'Поверхности отсутствуют'
		buttons = []
		for surface in self.app.equipment.surfaces:
			buttons.append([f'{surface.id}: {surface.type}', surface.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'])

	def show_surface(self):
		self.context = 'surface'
		text = f'номер поверхности: {self.surface.id}\nдата добавления: {self.surface.date}\n'
		text += f'тип: {self.surface.type}'
		buttons = []
		buttons.extend(['Удалить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Удалить', 'Назад'])

	def show_add_new_surface(self):
		self.context = 'add_new_surface'
		self.GUI.tell_buttons('Выберите тип поверхности', self.texts.surface_types.copy(), [])

	def show_add_confirmation(self):
		self.context = 'add_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить добавление')
		self.GUI.tell_buttons('Подтвердите добавление поверхности', buttons, ['Подтверждаю', 'Отменить добавление'])

	def show_delete_confirmation(self):
		self.context = 'delete_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить удаление')
		self.GUI.tell_buttons('Подтвердите удаление поверхности', buttons, ['Подтверждаю', 'Отменить удаление'])

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Добавить':
			self.show_add_new_surface()
		elif self.message.data == 'Назад':
			self.app.chat.user.employee.show_equipment()
		else:
			for surface in self.app.equipment.surfaces:
				if self.message.data == surface.id:
					self.surface = surface
					self.show_surface()

	def process_surface(self):
		self.context = ''
		if self.message.data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.data == 'Назад':
			self.show_top_menu()

	def process_add_new_surface(self):
		self.context = ''
		self.type = self.message.data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.surface = self.app.equipment.create_new_surface(self.type)
			text = f'Создана новая поверхность:\nномер: {self.surface.id}\nтип: {self.surface.type}\n\nНе забудьте нанести номер на поверхность.'
			self.GUI.tell(text)
		self.type = ''
		self.show_top_menu()

	def process_delete_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.GUI.tell(f'Поверхность {self.surface.id} удалена')
			self.app.equipment.remove_surface(self.surface.id)
			self.surface = None
		self.show_top_menu()