import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class PrinterGUI:
	app = None
	chat = None
	GUI = None
	printer = None

	name = ''

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

		elif context == 'printer':
			self.process_printer()

		elif context == 'add_new_printer':
			self.process_add_new_printer()
		elif context == 'add_confirmation':
			self.process_add_confirmation()
		elif context == 'delete_confirmation':
			self.process_delete_confirmation()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		if len(self.app.equipment.printers) > 0:
			text = 'Все принтеры:'
		else:
			text = 'Принтеры отсутствуют'
		buttons = []
		for printer in self.app.equipment.printers:
			buttons.append([f'{printer.id}: {printer.name}', printer.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'])

	def show_printer(self):
		self.context = 'printer'
		text = f'номер принтера: {self.printer.id}\nдата добавления: {self.printer.date}\n'
		text += f'название: {self.printer.name}\n'
		buttons = []
		buttons.extend(['Удалить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Удалить', 'Назад'])

	def show_add_new_printer(self):
		self.context = 'add_new_printer'
		self.GUI.tell('Введите название принтера')

	def show_add_confirmation(self):
		self.context = 'add_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить добавление')
		self.GUI.tell_buttons('Подтвердите добавление принтера', buttons, ['Подтверждаю', 'Отменить добавление'])

	def show_delete_confirmation(self):
		self.context = 'delete_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить удаление')
		self.GUI.tell_buttons('Подтвердите удаление принтера', buttons, ['Подтверждаю', 'Отменить удаление'])

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Добавить':
			self.show_add_new_printer()
		elif self.message.data == 'Назад':
			self.app.chat.user.employee.show_equipment()
		else:
			for printer in self.app.equipment.printers:
				if self.message.data == printer.id:
					self.printer = printer
					self.show_printer()

	def process_printer(self):
		self.context = ''
		if self.message.data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.data == 'Назад':
			self.show_top_menu()

	def process_add_new_printer(self):
		self.context = ''
		self.name = self.message.text
		self.show_add_confirmation()

	def process_add_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.printer = self.app.equipment.create_new_printer(self.name)
			text = f'Создан новый принтер:\nномер: {self.printer.id}\nназвание: {self.printer.name}\n'
			self.GUI.tell(text)
		self.name = ''
		self.type = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.GUI.tell(f'Принтер {self.printer.id} удален')
			self.app.equipment.remove_printer(self.printer.id)
			self.printer = None
		self.show_top_menu()