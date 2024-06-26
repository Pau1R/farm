import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class Printer_typeGUI:
	address = ''
	app = None
	chat = None
	GUI = None
	printer_type = None

	last_data = ''

	name = ''
	hour_cost = 0

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		data = message.data
		function = message.function
		if message.data_special_format and (data == '' or data != self.last_data):
			self.last_data = data
			if function == '1':
				self.process_top_menu()
			elif function == '2':
				self.process_printer_type()
			elif function == '3':
				self.process_add_name()
			elif function == '4':
				self.process_add_cost()
			elif function == '5':
				self.process_add_confirmation()
			elif function == '6':
				self.process_delete_confirmation()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.printer_types) > 0:
			text = 'Все типы принтеров:'
		else:
			text = 'Типы отсутствуют'
		buttons = []
		for printer_type in self.app.equipment.printer_types:
			buttons.append([printer_type.name, printer_type.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_printer_type(self):
		text = f'Название: {self.printer_type.name}\nСтоимость часа работы: {self.printer_type.hour_cost} рублей'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_add_name(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Введите название принтера')

	def show_add_cost(self):
		self.chat.set_context(self.address, 4)
		self.GUI.tell('Введите стоимость часа работы принтера в рублях')

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление типа принтера', buttons, buttons, 5, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление типа принтера', buttons, buttons, 6, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_name()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for printer_type in self.app.equipment.printer_types:
				if printer_type.id == int(self.message.btn_data):
					self.printer_type = printer_type
					self.show_printer_type()

	def process_printer_type(self):
		if self.message.btn_data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_name(self):
		self.name = self.message.text
		self.show_add_cost()

	def process_add_cost(self):
		try:
			self.hour_cost = int(self.message.text)
		except:
			self.GUI.tell('Неверные данные')
			self.show_add_cost()
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.printer_type = self.app.equipment.create_new_printer_type(self.name, self.hour_cost)
			text = f'Создан новый тип принтеров: {self.printer_type.name}'
			self.GUI.tell_permanent(text)
		self.name = ''
		self.type = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Тип принтера {self.printer_type.name} удален')
			self.app.equipment.remove_printer_type(self.printer_type.id)
			self.printer_type = None
		self.show_top_menu()