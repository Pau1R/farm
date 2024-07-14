import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui
import time

class BedGUI:
	context = ''
	last_data = ''

	type = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.bed = None

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
					self.process_bed()
				elif function == '3':
					self.process_add_new_bed()
				elif function == '4':
					self.process_add_confirmation()
				elif function == '5':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.beds) > 0:
			text = 'Все поверхности:'
		else:
			text = 'Поверхности отсутствуют'
		buttons = []
		for bed in self.app.equipment.beds:
			buttons.append([f'{bed.id}: {bed.type}', bed.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_bed(self):
		text = f'номер поверхности: {self.bed.id}\nдата добавления: {self.bed.created}\n'
		text += f'тип: {self.bed.type}'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_add_new_bed(self):
		buttons = ['PEI', 'Стекло']
		self.GUI.tell_buttons('Выберите тип поверхности', buttons, [], 3, 0)

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление поверхности', buttons, buttons, 4, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление поверхности', buttons, buttons, 5, 0)

	def show_busy(self):
		text = f'Поверхность находится в принтере {self.bed.location}'
		self.GUI.tell(text)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_bed()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for bed in self.app.equipment.beds:
				if bed.id == int(self.message.btn_data):
					self.bed = bed
					self.show_bed()

	def process_bed(self):
		if self.message.btn_data == 'Удалить':
			if self.bed.location_type == 'printer':
				self.show_busy()
				time.sleep(2)
				self.show_bed()
				return
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_new_bed(self):
		self.type = self.message.btn_data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.bed = self.app.equipment.create_new_bed(self.type)
			text = f'Создана новая поверхность:\nномер: {self.bed.id}\nтип: {self.bed.type}\n\nНе забудьте нанести номер на поверхность.'
			self.GUI.tell_permanent(text)
		self.type = ''
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Поверхность {self.bed.id} удалена')
			self.app.equipment.remove_bed(self.bed.id)
			self.bed = None
		self.show_top_menu()