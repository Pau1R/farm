import sys
sys.path.append('../lib')
from lib.Gui import Gui

class ContainerGUI:
	last_data = ''

	types = ['Сухой', 'Обычный']
	type = ''
	capacity = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.container = None

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				elif function == '2':
					self.process_container()
				elif function == '3':
					self.process_add_new_container()
				elif function == '4':
					self.process_add_new_container_capacity()
				elif function == '5':
					self.process_add_confirmation()
				elif function == '6':
					self.process_delete_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.equipment.containers) > 0:
			text = 'Все ящики:'
		else:
			text = 'Ящики отсутствуют'
		buttons = []
		for container in self.app.equipment.containers:
			buttons.append([str(container.id) + ': ' + container.type, container.id]) 
		buttons.append('Добавить')
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Добавить', 'Назад'], 1, 0)

	def show_container(self):
		text = f'Ящик номер {self.container.id}\nдата добавления: {self.container.created}\nтип: {self.container.type}\nемкость: {self.container.capacity} катушек'
		buttons = ['Удалить', 'Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, self.container.id)

	def show_add_new_container(self):
		buttons = []
		for type in self.types:
			buttons.append(type)
		self.GUI.tell_buttons('Выберите тип добавляемого ящика:', buttons, [], 3, 0)

	def show_add_new_container_capacity(self):
		buttons = []
		for capacity in range(0,10):
			buttons.append(str(capacity))
		self.GUI.tell_buttons('Выберите сколько катушек вмещает ящик:', buttons, [], 4, 0)

	def show_add_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление ящика', buttons, buttons, 5, 0)

	def show_delete_confirmation(self):
		buttons = ['Подтверждаю', 'Отменить удаление']
		self.GUI.tell_buttons('Подтвердите удаление ящика', buttons, buttons, 6, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Добавить':
			self.show_add_new_container()
		elif self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_equipment()
		else:
			for container in self.app.equipment.containers:
				if container.id == int(self.message.btn_data):
					self.container = container
					self.show_container()

	def process_container(self):
		if self.message.btn_data == 'Удалить':
			self.show_delete_confirmation()
		elif self.message.btn_data == 'Назад':
			self.show_top_menu()

	def process_add_new_container(self):
		self.type = self.message.btn_data
		self.show_add_new_container_capacity()

	def process_add_new_container_capacity(self):
		self.capacity = self.message.btn_data
		self.show_add_confirmation()

	def process_add_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.container = self.app.equipment.create_new_container(self.type, self.capacity)
			self.GUI.tell_permanent(f'Создан новый ящик\nномер: {self.container.id},\nтип: {self.container.type},\nемкость: {self.container.capacity} катушек\n\nНе забудьте нанести номер на ящик.')
		self.type = ''
		self.capacity = ''
		self.show_top_menu()

	def process_delete_confirmation(self):
		if self.message.btn_data == 'Подтверждаю':
			self.GUI.tell(f'Ящик {self.container.id} удален')
			self.app.equipment.remove_container(self.container.id)
			self.container = None
		self.show_top_menu()