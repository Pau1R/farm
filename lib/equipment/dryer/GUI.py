import sys
sys.path.append('../lib')
from lib.Gui import Gui

class DryerGUI:
	last_data = ''

	name = ''
	capacity = ''
	minTemp = ''
	maxTemp = ''
	maxTime = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.dryer = None

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
					self.process_dryer()
				elif function == '3':
					self.process_add_new_dryer()
				elif function == '4':
					self.process_add_new_dryer_capacity()
				elif function == '5':
					self.process_add_new_dryer_minTemp()
				elif function == '6':
					self.process_add_new_dryer_maxTemp()
				elif function == '7':
					self.process_add_new_dryer_maxTime()
				elif function == '8':
					self.process_add_confirmation()
				elif function == '9':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.dryers) > 0:
			text = 'Все сушилки:'
		else:
			text = 'Сушилки отсутствуют'
		buttons = []
		for dryer in self.app.equipment.dryers:
			buttons.append([str(dryer.id) + ': ' + dryer.name, dryer.id]) 
		buttons.append('Добавить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_dryer(self):
		text = f'Номер сушилки: {self.dryer.id}\nдата добавления: {self.dryer.created}\nназвание: {self.dryer.name}\nемкость: {self.dryer.capacity} катушек\n'
		text += f'минимальная температура: {self.dryer.minTemp}\nмаксимальная температура: {self.dryer.maxTemp}\n'
		text += f'максимальное время сушки: {self.dryer.maxTime}'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, ['Удалить', 'Назад'], 2, self.dryer.id)

	def show_add_new_dryer(self):
		self.chat.set_context(self.address, 3)
		self.GUI.tell('Введите название сушилки')

	def show_add_new_dryer_capacity(self):
		buttons = []
		for capacity in range(0,11):
			buttons.append(str(capacity))
		self.GUI.tell_buttons('Выберите сколько катушек вмещает сушилка:', buttons, [], 4, 0)

	def show_add_new_dryer_minTemp(self):
		buttons = []
		for temp in range(30, 101, 10):
			buttons.append(str(temp))
		self.GUI.tell_buttons('Выберите минимальную рабочую температуру сушилки:', buttons, [], 5, 0)

	def show_add_new_dryer_maxTemp(self):
		buttons = []
		for temp in range(60, 251, 10):
			buttons.append(str(temp))
		self.GUI.tell_buttons('Выберите максимальную рабочую температуру сушилки:', buttons, [], 6, 0)

	def show_add_new_dryer_maxTime(self):
		buttons = []
		for time in range(2, 11):
			buttons.append(str(time))
		self.GUI.tell_buttons('Выберите максимальное время таймера сушилки в часах:', buttons, [], 7, 0)

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление сушилки', buttons, buttons, 8, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление сушилки', buttons, buttons, 9, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_dryer()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for dryer in self.app.equipment.dryers:
				if dryer.id == int(self.message.btn_data):
					self.dryer = dryer
					self.show_dryer()

	def process_dryer(self):
		if self.message.btn_data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_new_dryer(self):
		self.name = self.message.text
		self.show_add_new_dryer_capacity()

	def process_add_new_dryer_capacity(self):
		self.capacity = self.message.btn_data
		self.show_add_new_dryer_minTemp()

	def process_add_new_dryer_minTemp(self):
		self.minTemp = self.message.btn_data
		self.show_add_new_dryer_maxTemp()

	def process_add_new_dryer_maxTemp(self):
		self.maxTemp = self.message.btn_data
		self.show_add_new_dryer_maxTime()

	def process_add_new_dryer_maxTime(self):
		self.maxTime = self.message.btn_data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.dryer = self.app.equipment.create_new_dryer(self.name, self.capacity, self.minTemp, self.maxTemp, self.maxTime)
			text = f'Создана новая сушилка:\nномер: {self.dryer.id}\nназвание: {self.dryer.name}\n'
			text += f'емкость: {self.dryer.capacity} катушки\nдиапазон температур: {self.dryer.minTemp}-{self.dryer.maxTemp}\n'
			text += f'максимальное время таймера: {self.dryer.maxTime}\n\nНе забудьте нанести номер на сушилку.'
			self.GUI.tell_permanent(text)
		self.type = ''
		self.capacity = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Сушилка {self.dryer.id} удалена')
			self.app.equipment.remove_dryer(self.dryer.id)
			self.dryer = None
		self.show_top_menu()