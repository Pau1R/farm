import sys
sys.path.append('../lib')
from lib.Gui import Gui

class DryerGUI:
	app = None
	chat = None
	GUI = None
	dryer = None

	name = ''
	capacity = ''
	minTemp = ''
	maxTemp = ''
	maxTime = ''

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

		elif context == 'dryer':
			self.process_dryer()

		elif context == 'add_new_dryer':
			self.process_add_new_dryer()
		elif context == 'add_new_dryer_capacity':
			self.process_add_new_dryer_capacity()
		elif context == 'add_new_dryer_minTemp':
			self.process_add_new_dryer_minTemp()
		elif context == 'add_new_dryer_maxTemp':
			self.process_add_new_dryer_maxTemp()
		elif context == 'add_new_dryer_maxTime':
			self.process_add_new_dryer_maxTime()
		elif context == 'add_confirmation':
			self.process_add_confirmation()
		
		elif context == 'delete_confirmation':
			self.process_delete_confirmation()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		if len(self.app.equipment.dryers) > 0:
			text = 'Все сушилки:'
		else:
			text = 'Сушилки отсутствуют'
		buttons = []
		for dryer in self.app.equipment.dryers:
			buttons.append([dryer.id + ': ' + dryer.name, dryer.id]) 
		buttons.append('Добавить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'])

	def show_dryer(self):
		self.context = 'dryer'
		text = f'Номер сушилки: {self.dryer.id}\nдата добавления: {self.dryer.date}\nназвание: {self.dryer.name}\nемкость: {self.dryer.capacity} катушек\n'
		text += f'минимальная температура: {self.dryer.minTemp}\nмаксимальная температура: {self.dryer.maxTemp}\n'
		text += f'максимальное время сушки: {self.dryer.maxTime}'
		buttons = []
		buttons.append('Удалить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Удалить', 'Назад'])

	def show_add_new_dryer(self):
		self.context = 'add_new_dryer'
		self.GUI.tell('Введите название сушилки')

	def show_add_new_dryer_capacity(self):
		self.context = 'add_new_dryer_capacity'
		buttons = []
		for capacity in range(0,11):
			buttons.append(str(capacity))
		self.GUI.tell_buttons('Выберите сколько катушек вмещает сушилка:', buttons, [])

	def show_add_new_dryer_minTemp(self):
		self.context = 'add_new_dryer_minTemp'
		buttons = []
		for temp in range(30, 101, 10):
			buttons.append(str(temp))
		self.GUI.tell_buttons('Выберите минимальную рабочую температуру сушилки:', buttons, [])

	def show_add_new_dryer_maxTemp(self):
		self.context = 'add_new_dryer_maxTemp'
		buttons = []
		for temp in range(60, 251, 10):
			buttons.append(str(temp))
		self.GUI.tell_buttons('Выберите максимальную рабочую температуру сушилки:', buttons, [])

	def show_add_new_dryer_maxTime(self):
		self.context = 'add_new_dryer_maxTime'
		buttons = []
		for time in range(2, 11):
			buttons.append(str(time))
		self.GUI.tell_buttons('Выберите максимальное время таймера сушилки в часах:', buttons, [])

	def show_add_confirmation(self):
		self.context = 'add_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить добавление')
		self.GUI.tell_buttons('Подтвердите добавление сушилки', buttons, ['Подтверждаю', 'Отменить добавление'])

	def show_delete_confirmation(self):
		self.context = 'delete_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить удаление')
		self.GUI.tell_buttons('Подтвердите удаление сушилки', buttons, ['Подтверждаю', 'Отменить удаление'])

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Добавить':
			self.show_add_new_dryer()
		elif self.message.data == 'Назад':
			self.app.chat.user.employee.show_equipment()
		else:
			for dryer in self.app.equipment.dryers:
				if self.message.data == dryer.id:
					self.dryer = dryer
					self.show_dryer()

	def process_dryer(self):
		self.context = ''
		if self.message.data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.data == 'Назад':
			self.show_top_menu()

	def process_add_new_dryer(self):
		self.context = ''
		self.name = self.message.text
		self.show_add_new_dryer_capacity()

	def process_add_new_dryer_capacity(self):
		self.context = ''
		self.capacity = self.message.data
		self.show_add_new_dryer_minTemp()

	def process_add_new_dryer_minTemp(self):
		self.context = ''
		self.minTemp = self.message.data
		self.show_add_new_dryer_maxTemp()

	def process_add_new_dryer_maxTemp(self):
		self.context = ''
		self.maxTemp = self.message.data
		self.show_add_new_dryer_maxTime()

	def process_add_new_dryer_maxTime(self):
		self.context = ''
		self.maxTime = self.message.data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.dryer = self.app.equipment.create_new_dryer(self.name, self.capacity, self.minTemp, self.maxTemp, self.maxTime)
			text = f'Создана новая сушилка:\nномер: {self.dryer.id}\nназвание: {self.dryer.name}\n'
			text += f'емкость: {self.dryer.capacity} катушки\nдиапазон температур: {self.dryer.minTemp}-{self.dryer.maxTemp}\n'
			text += f'максимальное время таймера: {self.dryer.maxTime}\n\nНе забудьте нанести номер на сушилку.'
			self.GUI.tell(text)
		self.type = ''
		self.capacity = 0
		self.show_top_menu()

	def process_delete_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.GUI.tell(f'Сушилка {self.dryer.id} удалена')
			self.app.equipment.remove_dryer(self.dryer.id)
			self.dryer = None
		self.show_top_menu()