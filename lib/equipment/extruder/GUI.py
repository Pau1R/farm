import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class ExtruderGUI:
	last_data = ''

	name = ''
	maxTemp = 0
	nozzleDiameter = 0.0

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.extruder = None

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
					self.process_extruder()
				elif function == '3':
					self.process_add_new_extruder()
				elif function == '4':
					self.process_add_new_extruder_maxTemp()
				elif function == '5':
					self.process_add_new_extruder_nozzleDiameter()
				elif function == '6':
					self.process_add_confirmation()
				elif function == '7':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.extruders) > 0:
			text = 'Все экструдеры:'
		else:
			text = 'Экструдеры отсутствуют'
		buttons = []
		for extruder in self.app.equipment.extruders:
			buttons.append([str(extruder.id) + ': ' + extruder.name, extruder.id]) 
		buttons.append('Добавить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_extruder(self):
		text = f'номер экструдера: {self.extruder.id}\nдата добавления: {self.extruder.created}\nназвание: {self.extruder.name}\n'
		text += f'максимальная температура: {self.extruder.maxTemp}\n'
		text += f'диаметр сопла: {self.extruder.nozzleDiameter}'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, self.extruder.id)

	def show_add_new_extruder(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Введите название экструдера')

	def show_add_new_extruder_maxTemp(self):
		buttons = []
		for temp in range(200, 401, 10):
			buttons.append(str(temp))
		self.GUI.tell_buttons('Выберите максимальную температуру сопла:', buttons, [], 4, 0)

	def show_add_new_extruder_nozzleDiameter(self):
		buttons = []
		for temp in numpy.arange(0.2, 1.3, 0.1):
			buttons.append(str(round(temp, 2)))
		self.GUI.tell_buttons('Выберите диаметр сопла:', buttons, [], 5, 0)

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление экструдера', buttons, buttons, 6, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление экструдера', buttons, buttons, 7, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_extruder()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for extruder in self.app.equipment.extruders:
				if extruder.id == int(self.message.btn_data):
					self.extruder = extruder
					self.show_extruder()

	def process_extruder(self):
		if self.message.btn_data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_new_extruder(self):
		self.name = self.message.text
		self.show_add_new_extruder_maxTemp()

	def process_add_new_extruder_maxTemp(self):
		self.maxTemp = int(self.message.btn_data)
		self.show_add_new_extruder_nozzleDiameter()

	def process_add_new_extruder_nozzleDiameter(self):
		self.nozzleDiameter = float(self.message.btn_data)
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.extruder = self.app.equipment.create_new_extruder(self.name, self.maxTemp, self.nozzleDiameter)
			text = f'Создан новый экструдер:\nномер: {self.extruder.id}\nназвание: {self.extruder.name}\n'
			text += f'максимальная температура: {self.extruder.maxTemp}\nдиаметр сопла: {self.extruder.nozzleDiameter}'
			text += f'\n\nНе забудьте нанести номер на экструдер.'
			self.GUI.tell_permanent(text)
		self.name = ''
		self.maxTemp = 0
		self.nozzleDiameter = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Экструдер {self.extruder.id} удален')
			self.app.equipment.remove_extruder(self.extruder.id)
			self.extruder = None
		self.show_top_menu()