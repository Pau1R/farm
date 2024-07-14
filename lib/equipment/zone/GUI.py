import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class ZoneGUI:
	last_data = ''

	name = ''
	type = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.zone = None

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
					self.process_zone()
				elif function == '3':
					self.process_add_new_zone()
				elif function == '4':
					self.process_add_new_zone_type()
				elif function == '5':
					self.process_add_confirmation()
				elif function == '6':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.zones) > 0:
			text = 'Все локации:'
		else:
			text = 'Локации отсутствуют'
		buttons = []
		for zone in self.app.equipment.zones:
			buttons.append([f'{zone.id}: {zone.type} {zone.name}', zone.id]) 
		buttons.extend(['Добавить', 'Назад'])
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_zone(self):
		text = f'номер локации: {self.zone.id}\nдата добавления: {self.zone.created}\n'
		text += f'название: {self.zone.name}\nтип: {self.zone.type}\n'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_add_new_zone(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Введите название локации')

	def show_add_new_zone_type(self):
		buttons = ['Помещение', 'Зона']
		self.GUI.tell_buttons('Выберите тип локации:', buttons, [], 4, 0)

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление локации', buttons, buttons, 5, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление локации', buttons, buttons, 6, 0)

	def show_busy(self):
		content = self.location.readable_content()
		self.GUI.tell(f'Удалить нельзя - локация не пустая:\n{content.lower()}')

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_zone()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for zone in self.app.equipment.zones:
				if zone.id == int(self.message.btn_data):
					self.zone = zone
					self.show_zone()

	def process_zone(self):
		if self.message.btn_data == 'Удалить':
			self.location = self.app.locations.get('zone', self.zone.id)
			if self.location.empty():
				self.show_delete_confirmation()
			else:
				self.show_busy()
				self.last_data = ''
				self.show_zone()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_new_zone(self):
		self.name = self.message.text
		self.show_add_new_zone_type()

	def process_add_new_zone_type(self):
		self.type = self.message.btn_data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.zone = self.app.equipment.create_new_zone(self.name, self.type)
			text = f'Создана новая локация:\nномер: {self.zone.id}\nназвание: {self.zone.name}\n'
			text += f'тип: {self.zone.type}'
			self.GUI.tell_permanent(text)
		self.name = ''
		self.type = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Локация {self.zone.id} удалена')
			self.app.equipment.remove_zone(self.zone.id)
			self.zone = None
		self.show_top_menu()