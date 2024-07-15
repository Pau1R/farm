import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class PrinterGUI:
	context = ''
	last_data = ''

	name = ''
	type_ = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.printer = None

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
					self.process_printer()
				elif function == '3':
					self.process_type()
				elif function == '4':
					self.process_name()
				elif function == '5':
					self.process_locations()
				elif function == '6':
					self.process_add_confirmation()
				elif function == '7':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

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
		text = f'номер принтера: {self.printer.id}\nдата добавления: {self.printer.created}\n'
		text += f'название: {self.printer.name}\nтип: {self.printer.type_}'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_type(self):
		buttons = []
		for type_ in self.app.equipment.printer_types:
			buttons.append([type_.name, type_.id])
		self.GUI.tell_buttons('Выберите тип принтера', buttons, buttons, 3, 0)

	def show_name(self):
		self.chat.set_context(self.address, 4)
		self.GUI.tell('Введите название принтера')

	def show_locations(self):
		text = f'Выберите локацию'
		buttons = self.app.locations.get_buttons('zone')
		self.GUI.tell_buttons(text, buttons, buttons, 5, 0)

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление принтера', buttons, buttons, 6, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление принтера', buttons, buttons, 7, 0)

	def show_busy(self):
		content = self.location.readable_content()
		self.GUI.tell(f'Удалить нельзя - принтер не пустой:\n{content.lower()}')

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_type()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.last_data = ''
			self.app.chat.user.admin.show_equipment()
		else:
			for printer in self.app.equipment.printers:
				if printer.id == int(self.message.btn_data):
					self.printer = printer
					self.show_printer()

	def process_printer(self):
		if self.message.btn_data == 'Удалить':
			self.location = self.app.locations.get_location('printer', self.printer.id)
			if self.location.empty():
				self.show_delete_confirmation()
			else:
				self.show_busy()
				self.last_data = ''
				self.show_printer()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_type(self):
		self.type_ = self.message.btn_data
		self.show_name()

	def process_name(self):
		self.name = self.message.text
		self.show_locations()
	
	def process_locations(self):
		self.location = int(self.message.btn_data)
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.printer = self.app.equipment.create_new_printer(self.name, self.type_)
			self.printer.location_type = 'zone'
			self.printer.location = self.location
			self.app.db.update_printer(self.printer)
			text = f'Создан новый принтер:\nномер: {self.printer.id}\nназвание: {self.printer.name}\nтип: {self.printer.type_}'
			self.GUI.tell_permanent(text)
		self.name = ''
		self.type = 0
		self.location = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Принтер {self.printer.id} удален')
			self.app.equipment.remove_printer(self.printer.id)
			self.printer = None
		self.show_top_menu()