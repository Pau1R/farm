import numpy
import sys
sys.path.append('../lib')
from lib.Gui import Gui

class ExtruderGUI:
	app = None
	chat = None
	GUI = None
	extruder = None

	name = ''
	maxTemp = 0
	nozzleDiameter = 0

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

		elif context == 'extruder':
			self.process_extruder()

		elif context == 'add_new_extruder':
			self.process_add_new_extruder()
		elif context == 'add_new_extruder_maxTemp':
			self.process_add_new_extruder_maxTemp()
		elif context == 'add_new_extruder_nozzleDiameter':
			self.process_add_new_extruder_nozzleDiameter()
		elif context == 'add_confirmation':
			self.process_add_confirmation()
		elif context == 'delete_confirmation':
			self.process_delete_confirmation()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		if len(self.app.equipment.extruders) > 0:
			text = 'Все экструдеры:'
		else:
			text = 'Экструдеры отсутствуют'
		buttons = []
		for extruder in self.app.equipment.extruders:
			buttons.append([extruder.id + ': ' + extruder.name, extruder.id]) 
		buttons.append('Добавить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'])

	def show_extruder(self):
		self.context = 'extruder'
		text = f'номер экструдера: {self.extruder.id}\nдата добавления: {self.extruder.date}\nназвание: {self.extruder.name}\n'
		text += f'максимальная температура: {self.extruder.maxTemp}\n'
		text += f'диаметр сопла: {self.extruder.nozzleDiameter}'
		buttons = []
		buttons.append('Удалить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Удалить', 'Назад'])

	def show_add_new_extruder(self):
		self.context = 'add_new_extruder'
		self.GUI.tell('Введите название экструдера')

	def show_add_new_extruder_maxTemp(self):
		self.context = 'add_new_extruder_maxTemp'
		buttons = []
		for temp in range(200, 401, 10):
			buttons.append(str(temp))
		self.GUI.tell_buttons('Выберите максимальную температуру сопла:', buttons, [])

	def show_add_new_extruder_nozzleDiameter(self):
		self.context = 'add_new_extruder_nozzleDiameter'
		buttons = []
		for temp in numpy.arange(0.2, 1.3, 0.1):
			buttons.append(str(round(temp, 2)))
		self.GUI.tell_buttons('Выберите диаметр сопла:', buttons, [])

	def show_add_confirmation(self):
		self.context = 'add_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить добавление')
		self.GUI.tell_buttons('Подтвердите добавление экструдера', buttons, ['Подтверждаю', 'Отменить добавление'])

	def show_delete_confirmation(self):
		self.context = 'delete_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить удаление')
		self.GUI.tell_buttons('Подтвердите удаление ящика', buttons, ['Подтверждаю', 'Отменить удаление'])

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Добавить':
			self.show_add_new_extruder()
		elif self.message.data == 'Назад':
			self.app.chat.user.employee.show_equipment()
		else:
			for extruder in self.app.equipment.extruders:
				if self.message.data == extruder.id:
					self.extruder = extruder
					self.show_extruder()

	def process_extruder(self):
		self.context = ''
		if self.message.data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.data == 'Назад':
			self.show_top_menu()

	def process_add_new_extruder(self):
		self.context = ''
		self.name = self.message.text
		self.show_add_new_extruder_maxTemp()

	def process_add_new_extruder_maxTemp(self):
		self.context = ''
		self.maxTemp = self.message.data
		self.show_add_new_extruder_nozzleDiameter()

	def process_add_new_extruder_nozzleDiameter(self):
		self.context = ''
		self.nozzleDiameter = self.message.data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.extruder = self.app.equipment.create_new_extruder(self.name, self.maxTemp, self.nozzleDiameter)
			text = f'Создан новый экструдер:\nномер: {self.extruder.id}\nназвание: {self.extruder.name}\n'
			text += f'максимальная температура: {self.extruder.maxTemp}\nдиаметр сопла: {self.extruder.nozzleDiameter}'
			text += f'\n\nНе забудьте нанести номер на экструдер.'
			self.GUI.tell(text)
		self.name = ''
		self.maxTemp = 0
		self.nozzleDiameter = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.GUI.tell(f'Экструдер {self.extruder.id} удален')
			self.app.equipment.remove_extruder(self.extruder.id)
			self.extruder = None
		self.show_top_menu()