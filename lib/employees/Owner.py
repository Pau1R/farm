import time
import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.Texts import Texts

# Владелец добавляет/удаляет сотрудников и получает отчеты

class Owner:
	app = None
	chat = None
	GUI = None
	message = None
	context = ''
	employees = []
	employee = None
	new_employee_id = ''
	texts = Texts()

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
			self.show_top_menu() # 'top_menu'

		if context == 'top_menu':
			self.process_top_menu() # 'employees' 'add_employees' 'statistics'

		if context == 'add_employees':
			self.process_add_employee()
		
		if context == 'employee_ownership_confirmation':
			self.process_employee_ownership_confirmation()

		if context == 'add_employee_confirmation':
			self.process_add_employee_confirmation()

		if context == 'employees':
			self.process_employees()

		if context == 'employee':
			self.process_employee() # 'employee_statistics'

		if context == 'add_employee_role':
			self.process_add_employee_role()

		if context == 'delete_employee_role':
			self.process_delete_employee_role()

		if context == 'employee_delete_confirmation':
			self.process_employee_delete_confirmation()

	def show_top_menu(self):
		self.context = 'top_menu'
		text = 'Здравствуйте, владелец ' + self.chat.user.name
		buttons = ['Сотрудники', 'Статистика']
		for obj in self.app.chats:
			if obj.get_employed:
				buttons.append('Запросы')
		self.GUI.tell_buttons(text, buttons, [])

	def process_top_menu(self):
		self.context = ''
		if self.message.data == 'Сотрудники':
			self.show_employees() # 'employees'
		elif self.message.data == 'Запросы':
			self.show_add_employees() # 'add_employees'
		elif self.message.data == 'Статистика':
			self.show_farm_statistics()

#---------------------------- SHOW EMPLOYEES ----------------------------

	def show_employees(self):
		self.context = 'employees'
		buttons = []
		for obj in self.app.chats:
			print('is_employee', obj.is_employee)
			if obj.is_employee:
				self.employees.append(obj)
				buttons.append([obj.user.role + ': ' + obj.user.name, obj.user_id])
		buttons.append('Назад')
		self.GUI.tell_buttons(self.texts.owner_employee_menu, buttons, ['Назад'])

	def show_employee(self):
		self.context = 'employee'
		if self.employee == None:
			for obj in self.employees:
				if obj.user_id == self.message.data:
					self.employee = obj
		self.employees = []
		text = 'Имя: ' + self.employee.user.name + '\nРоли: ' + str(self.employee.user.roles.copy()) + '\nДата создания: ' + self.employee.created  # add additional info in future
		buttons = ['Статистика', 'Удалить', 'Сделать владельцем вместо себя', 'Добавить роль', 'Удалить роль', 'Назад']
		if 'Владелец' in self.employee.user.roles:
			buttons.remove('Удалить')
			buttons.remove('Сделать владельцем вместо себя')
		if len([i for i in self.employee.user.roles if i not in 'Владелец']) == 4:
			buttons.remove('Добавить роль')
		elif len([i for i in self.employee.user.roles if i not in 'Владелец']) == 0:
			buttons.remove('Удалить роль')
		self.GUI.tell_buttons(text, buttons, ['Назад'])

	def show_employee_ownership_confirmation(self):
		self.context = 'employee_ownership_confirmation'
		buttons = ['Подтвердить', 'Отменить']
		self.GUI.tell_buttons('Подтвердите передачу права владения', buttons, [])

	def show_add_employees(self):
		self.context = 'add_employees'
		buttons = []
		for obj in self.app.chats:
			if obj.get_employed:
				buttons.append([obj.user.name, obj.user_id])
		buttons.append('Назад')
		text = 'Добавьте сотрудника:'
		self.GUI.tell_buttons(text, buttons, ['Назад'])

	def show_add_employee_confirmation(self):
		self.context = 'add_employee_confirmation'
		buttons = ['Подтвердить', 'Отменить добавление']
		self.GUI.tell_buttons('Подтвердите добавление сотрудника', buttons, [])

	def show_employee_statistics(self):
		self.context = 'employee_statistics'
		self.GUI.tell('Модуль статистики будет доработан в будущем')
		time.sleep(2)
		self.GUI.clear_chat()
		self.show_employee()

	def show_employee_roles(self, isAdd):
		roles = ['Администратор', 'Оператор', 'Дизайнер', 'Выдача']
		if isAdd:
			self.context = 'add_employee_role'
			buttons = [i for i in roles if i not in self.employee.user.roles]
			text = 'Какую роль вы хотите добавить пользователю ' + self.employee.user.name + '?'
		else:
			self.context = 'delete_employee_role'
			# buttons = self.employee.user.roles.copy()
			buttons = [i for i in self.employee.user.roles if i not in 'Владелец']
			text = 'Какую роль вы хотите удалить для пользователя ' + self.employee.user.name + '?'
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, ['Назад'])

	def show_employee_delete_confirmation(self):
		self.context = 'employee_delete_confirmation'
		text = 'Вы уверены, что хотите удалить сотрудника: ' + self.employee.user.name + '?'
		buttons = ['Да, удалить', 'Отмена']
		self.GUI.tell_buttons(text, buttons, ['Да, удалить', 'Отмена'])

#---------------------------- PROCESS EMPLOYEES ----------------------------

	def process_employees(self):
		if self.message.data == 'Назад':
			self.show_top_menu()
		else:
			self.show_employee() # 'employee'

	def process_employee(self):
		data = self.message.data
		if data == 'Удалить':
			self.show_employee_delete_confirmation()  # TODO: function untested, test
		elif data == 'Статистика':
			self.show_employee_statistics()
		elif data == 'Сделать владельцем вместо себя': # TODO: add timeout before confirmation
			self.show_employee_ownership_confirmation()
		elif data == 'Добавить роль':
			self.show_employee_roles(True)
		elif data == 'Удалить роль':
			self.show_employee_roles(False)
		elif data == 'Назад':
			self.context = ''
			self.employee = None
			self.show_employees()

	def process_employee_ownership_confirmation(self):
		data = self.message.data
		if data == 'Отменить':
			self.show_employee()
		if data == 'Подтвердить':
			self.app.chat.user.roles = [i for i in self.app.chat.user.roles if i not in 'Владелец']
			self.app.db.delete_employee_role(self.app.chat.user_id, 'Владелец')
			self.employee.user.roles.append('Владелец')
			self.app.db.add_employee_role(self.employee.user_id, 'Владелец')
			self.GUI.tell(f'Пользователю {self.employee.user.name} передано право владельца чат-бота')
			self.GUI.tell_id(self.employee.user_id, 'Вам переданы права владельца')
			self.message.text = '/start'
			self.app.chat.user.new_message(self.message)

	def process_add_employee(self):
		if self.message.data == 'Назад':
			self.show_top_menu()
		else:
			self.new_employee_id = self.message.data
			self.show_add_employee_confirmation()

	def process_add_employee_confirmation(self):
		if self.message.data == 'Отменить добавление':
			self.show_top_menu()
		elif self.message.data == 'Подтвердить':
			for obj in self.app.chats:
				if obj.user_id == self.new_employee_id:
					obj.become_employee()
					self.app.db.update_chat(obj)
					# self.db.add_employee(obj.user_id, obj.user.name)
					self.GUI.tell_id(obj.user_id, 'Вы стали сотрудником, поздравляем!')
			self.show_top_menu()

	def process_add_employee_role(self):
		if self.message.data != 'Назад':
			self.employee.user.roles.append(self.message.data)
			self.app.db.update_chat(self.employee)
			self.GUI.tell_id(self.employee.user_id, 'Вам добавлена роль: ' + self.message.data)
		self.context = ''
		self.show_employee()

	def process_delete_employee_role(self):
		if self.message.data != 'Назад':
			self.employee.user.roles = [i for i in self.employee.user.roles if i not in self.message.data]
			self.app.db.update_chat(self.employee)
			self.GUI.tell_id(self.employee.user_id, 'Ваша роль ' + self.message.data + ' удалена')
		self.context = ''
		self.show_employee()

	def process_employee_delete_confirmation(self):
		if self.message.data != 'Отмена':
			self.employee.is_employee = False
			self.employee.user.roles = []
			self.employee.user.name = ''
			# self.db.delete_employee(self.employee.user_id)
			self.app.db.remove_chat(self.employee)
			self.GUI.tell_id(self.employee.user_id, 'Ваше сотрудничество окончено, всего хорошего')
			self.employee = None
			self.show_employees()
		else:
			self.context = ''
			self.show_employee()

#---------------------------- OTHER ----------------------------

	def show_farm_statistics(self):
		self.GUI.tell('Модуль статистики будет доработан в будущем')
		time.sleep(2)
		self.GUI.clear_chat()
		self.show_top_menu()