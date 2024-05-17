import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class PrinterGUI:
	address = '1/2/5'
	app = None
	chat = None
	GUI = None
	printer = None

	context = ''
	last_data = ''

	name = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)

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
				self.process_printer()
			elif message.function == '3':
				self.process_add_new_printer()
			elif message.function == '4':
				self.process_add_confirmation()
			elif message.function == '5':
				self.process_delete_confirmation()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.printers) > 0:
			text = 'Все принтеры:'
		else:
			text = 'Принтеры отсутствуют'
		buttons = []
		for printer in self.app.equipment.printers:
			buttons.append([f'{printer.id}: {printer.name}', printer.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_printer(self):
		text = f'номер принтера: {self.printer.id}\nдата добавления: {self.printer.date}\n'
		text += f'название: {self.printer.name}\n'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_add_new_printer(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Введите название принтера')

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление принтера', buttons, buttons, 4, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление принтера', buttons, buttons, 5, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_printer()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for printer in self.app.equipment.printers:
				if self.message.btn_data == printer.id:
					self.printer = printer
					self.show_printer()

	def process_printer(self):
		if self.message.btn_data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_new_printer(self):
		self.name = self.message.text
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.printer = self.app.equipment.create_new_printer(self.name)
			text = f'Создан новый принтер:\nномер: {self.printer.id}\nназвание: {self.printer.name}\n'
			self.GUI.tell_permanent(text)
		self.name = ''
		self.type = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Принтер {self.printer.id} удален')
			self.app.equipment.remove_printer(self.printer.id)
			self.printer = None
		self.show_top_menu()