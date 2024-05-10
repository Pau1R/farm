import sys
sys.path.append('../lib')
from lib.Gui import Gui

class ContainerGUI:
	app = None
	chat = None
	GUI = None
	container = None

	types = ['Сухой', 'Обычный']
	type = ''
	capacity = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat)

	def first_message(self, message):
		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.messages_append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_top_menu()
		elif context == 'top_menu':
			self.process_top_menu()
		elif context == 'container':
			self.process_container()
		elif context == 'add_new_container':
			self.process_add_new_container()
		elif context == 'add_new_container_capacity':
			self.process_add_new_container_capacity()
		elif context == 'add_confirmation':
			self.process_add_confirmation()
		elif context == 'delete_confirmation':
			self.process_delete_confirmation()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		if len(self.app.equipment.containers) > 0:
			text = 'Все ящики:'
		else:
			text = 'Ящики отсутствуют'
		buttons = []
		for container in self.app.equipment.containers:
			buttons.append([container.id + ': ' + container.type, container.id]) 
		buttons.append('Добавить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'])

	def show_container(self):
		self.context = 'container'
		text = f'Ящик номер {self.container.id}\nдата добавления: {self.container.date}\nтип: {self.container.type}\nемкость: {self.container.capacity} катушек'
		buttons = []
		buttons.append('Удалить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Удалить', 'Назад'])

	def show_add_new_container(self):
		self.context = 'add_new_container'
		buttons = []
		for type in self.types:
			buttons.append(type)
		self.GUI.tell_buttons('Выберите тип добавляемого ящика:', buttons, [])

	def show_add_new_container_capacity(self):
		self.context = 'add_new_container_capacity'
		buttons = []
		for capacity in range(0,10):
			buttons.append(str(capacity))
		self.GUI.tell_buttons('Выберите сколько катушек вмещает ящик:', buttons, [])

	def show_add_confirmation(self):
		self.context = 'add_confirmation'
		buttons = []
		buttons.append('Подтверждаю')
		buttons.append('Отменить добавление')
		self.GUI.tell_buttons('Подтвердите добавление ящика', buttons, ['Подтверждаю', 'Отменить добавление'])

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
			self.show_add_new_container()
		elif self.message.data == 'Назад':
			self.app.chat.user.employee.show_equipment()
		else:
			for container in self.app.equipment.containers:
				if self.message.data == container.id:
					self.container = container
					self.show_container()

	def process_container(self):
		self.context = ''
		if self.message.data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.data == 'Назад':
			self.show_top_menu()

	def process_add_new_container(self):
		self.context = ''
		self.type = self.message.data
		self.show_add_new_container_capacity()

	def process_add_new_container_capacity(self):
		self.context = ''
		self.capacity = self.message.data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.container = self.app.equipment.create_new_container(self.type, self.capacity)
			self.GUI.tell(f'Создан новый ящик\nномер: {self.container.id},\nтип: {self.container.type},\nемкость: {self.container.capacity} катушек\n\nНе забудьте нанести номер на ящик.')
		self.type = ''
		self.capacity = ''
		self.show_top_menu()

	def process_delete_confirmation(self):
		self.context = ''
		if self.message.data == 'Подтверждаю':
			self.GUI.tell(f'Ящик {self.container.id} удален')
			self.app.equipment.remove_container(self.container.id)
			self.container = None
		self.show_top_menu()