import time
import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.Texts import Texts

class Owner:
	address = ''

	app = None
	chat = None
	GUI = None
	message = None
	last_data = ''
	employees = []
	employee = None
	new_employee_id = ''
	texts = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.messages_append(message)
		self.message = message

		function = message.function
		if message.data_special_format:
			if self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				elif function == '2':
					self.process_add_employee()
				elif function == '3':
					self.process_employee_ownership_confirmation()
				elif function == '4':
					self.process_add_employee_confirmation()
				elif function == '5':
					self.process_employees()
				elif function == '6':
					self.process_employee()
				elif function == '7':
					self.process_add_employee_role()
				elif function == '8':
					self.process_delete_employee_role()
				elif function == '9':
					self.process_employee_delete_confirmation()
		self.chat.add_if_text(self)

	def show_top_menu(self):
		text = 'Здравствуйте, владелец ' + self.chat.user_name
		buttons = ['Сотрудники', 'Статистика']
		for chat in self.app.chats:
			if chat.get_employed:
				buttons.append('Запросы')
		if len(self.chat.user.roles) > 1:
			buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'], 1, 0)

	def process_top_menu(self):
		if self.message.btn_data == 'Сотрудники':
			self.show_employees()
		elif self.message.btn_data == 'Запросы':
			self.show_add_employees()
		elif self.message.btn_data == 'Статистика':
			self.show_farm_statistics()
		elif self.message.btn_data == 'Назад':
			self.message.text = '/start'
			self.chat.user.new_message(self.message)

#---------------------------- SHOW EMPLOYEES ----------------------------

	def show_employees(self):
		buttons = []
		for chat in self.app.chats:
			if chat.is_employee:
				self.employees.append(chat)
				buttons.append([chat.user_name, chat.user_id])
		buttons.append('Назад')
		self.GUI.tell_buttons(self.texts.owner_employee_menu, buttons, ['Назад'], 5, 0)

	def show_employee(self):
		if self.employee == None:
			for chat in self.employees:
				if str(chat.user_id) == self.message.btn_data:
					self.employee = chat
		self.employees = []
		text = 'Имя: ' + self.employee.user_name + '\nРоли: ' + str(self.employee.user.roles.copy()) + '\nДата создания: ' + self.employee.created  # add additional info in future
		buttons = ['Статистика', 'Удалить', ['Сделать владельцем вместо себя', 'tranfer_ownership'], 'Добавить роль', 'Удалить роль', 'Назад']
		if 'Владелец' in self.employee.user.roles:
			buttons.remove('Удалить')
			buttons.remove(['Сделать владельцем вместо себя', 'tranfer_ownership'])
		if len([i for i in self.employee.user.roles if i not in 'Владелец']) == 4:
			buttons.remove('Добавить роль')
		elif len([i for i in self.employee.user.roles if i not in 'Владелец']) == 0:
			buttons.remove('Удалить роль')
		self.GUI.tell_buttons(text, buttons, ['Назад'], 6, self.employee.user_id)

	def show_employee_ownership_confirmation(self):
		buttons = ['Подтвердить', 'Отменить']
		self.GUI.tell_buttons('Подтвердите передачу права владения', buttons, [], 3, self.employee.user_id)

	def show_add_employees(self):
		buttons = []
		for chat in self.app.chats:
			if chat.get_employed:
				buttons.append([chat.user_name, chat.user_id])
		buttons.append('Назад')
		text = 'Добавьте сотрудника:'
		self.GUI.tell_buttons(text, buttons, ['Назад'], 2, 0)

	def show_add_employee_confirmation(self, message):
		buttons = ['Подтвердить', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление сотрудника', buttons, [], 4, message.instance_id)

	def show_employee_statistics(self):
		self.GUI.tell('Модуль статистики будет доработан в будущем')
		time.sleep(2)
		self.GUI.clear_chat()
		self.show_employee()

	def show_employee_roles(self, isAdd):
		roles = ['Администратор', 'Оператор', 'Дизайнер', 'Выдача']
		if isAdd:
			function_id = 7
			buttons = [i for i in roles if i not in self.employee.user.roles]
			text = 'Какую роль вы хотите добавить пользователю ' + self.employee.user_name + '?'
		else:
			function_id = 8
			buttons = [i for i in self.employee.user.roles if i not in 'Владелец']
			text = 'Какую роль вы хотите удалить для пользователя ' + self.employee.user_name + '?'
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'], function_id, self.employee.user_id)

	def show_employee_delete_confirmation(self):
		text = 'Вы уверены, что хотите удалить сотрудника: ' + self.employee.user_name + '?'
		buttons = ['Да, удалить', 'Отмена']
		self.GUI.tell_buttons(text, buttons, ['Да, удалить', 'Отмена'], 9, self.employee.user_id)

#---------------------------- PROCESS EMPLOYEES ----------------------------

	def process_employees(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		else:
			self.show_employee()

	def process_employee(self):
		data = self.message.btn_data
		if data == 'Удалить':
			self.show_employee_delete_confirmation()
		elif data == 'Статистика':
			self.show_employee_statistics()
		elif data == 'tranfer_ownership':
			self.show_employee_ownership_confirmation()
		elif data == 'Добавить роль':
			self.show_employee_roles(True)
		elif data == 'Удалить роль':
			self.show_employee_roles(False)
		elif data == 'Назад':
			self.employee = None
			self.show_employees()

	def process_employee_ownership_confirmation(self):
		data = self.message.btn_data
		if data == 'Отменить':
			self.show_employee()
		if data == 'Подтвердить':
			self.app.chat.user.roles = [i for i in self.app.chat.user.roles if i not in 'Владелец']
			self.app.db.delete_employee_role(self.app.chat.user_id, 'Владелец')
			self.employee.user.roles.append('Владелец')
			self.app.db.add_employee_role(self.employee.user_id, 'Владелец')
			self.GUI.tell(f'Пользователю {self.employee.user_name} передано право владельца чат-бота')
			self.GUI.tell_id(self.employee.user_id, 'Вам переданы права владельца')
			self.message.text = '/start'
			self.app.chat.user.new_message(self.message)

	def process_add_employee(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		else:
			self.message.instance_id = self.message.btn_data
			self.show_add_employee_confirmation(self.message)

	def process_add_employee_confirmation(self):
		chat = self.app.get_chat(self.message.instance_id)
		if self.message.btn_data == 'Отменить добавление':
			chat.get_employed = False
			self.app.db.update_chat(chat)
			self.show_top_menu()
		elif self.message.btn_data == 'Подтвердить':
			chat.user.show_becomes_employee()
			chat.become_employee()
			self.show_top_menu()

	def process_add_employee_role(self):
		if self.message.btn_data != 'Назад':
			self.employee.user.roles.append(self.message.btn_data)
			self.app.db.update_chat(self.employee)
			self.GUI.tell_id(self.employee.user_id, 'Вам добавлена роль: ' + self.message.btn_data)
		self.show_employee()

	def process_delete_employee_role(self):
		if self.message.btn_data != 'Назад':
			self.employee.user.roles = [i for i in self.employee.user.roles if i not in self.message.btn_data]
			self.app.db.update_chat(self.employee)
			self.GUI.tell_id(self.employee.user_id, 'Ваша роль ' + self.message.btn_data + ' удалена')
		self.show_employee()

	def process_employee_delete_confirmation(self):
		if self.message.btn_data != 'Отмена':
			self.employee.is_employee = False
			self.employee.user.roles = []
			self.employee.user_name = ''
			self.app.db.remove_chat(self.employee)
			self.GUI.tell_id(self.employee.user_id, 'Вы перестали быть сотрудником')
			self.app.chats.remove(self.employee)
			self.employee = None
			self.show_employees()
		else:
			self.show_employee()

#---------------------------- OTHER ----------------------------

	def show_farm_statistics(self):
		self.GUI.tell('Модуль статистики будет доработан в будущем')
		time.sleep(2)
		self.GUI.clear_chat()
		self.show_top_menu()