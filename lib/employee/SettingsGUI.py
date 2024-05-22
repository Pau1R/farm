import sys
sys.path.append('../lib')
from lib.Gui import Gui

class SettingsGUI:
	address = '1/2/9'

	app = None
	chat = None
	GUI = None

	last_data = ''

	name = ''
	value = ''

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
			elif message.function == '2':
				self.process_settings_money()
			elif message.function == '3':
				self.process_setting()
			elif message.function == '4':
				self.process_confirmation()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		buttons = [['Финансы', 'money'], 'Назад']
		self.GUI.tell_buttons('Выберите категорию', buttons, ['Назад'], 1, 0)

	def show_settings_money(self):
		buttons = []
		param = 'support_remove_price'
		text = 'Стоимость одной минуты удаления поддержек: ' + self.app.settings.get(param) + ' рублей'
		buttons.append([text, param])
		param = 'prepayment_percent'
		text = 'Процент предоплаты: ' + self.app.settings.get(param) + '%'
		buttons.append([text, param])
		param = 'prepayment_free_max'
		text = 'Максимальная сумма без предоплаты: ' + self.app.settings.get(param) + ' рублей'
		buttons.append([text, param])
		param = 'phone_number'
		text = 'Телефон для переводов: ' + self.app.settings.get(param)
		buttons.append([text, param])
		param = 'card_number'
		text = 'Карточка для переводов: ' + self.app.settings.get(param)
		buttons.append([text, param])
		param = 'account_number'
		text = 'Счет для переводов: ' + self.app.settings.get(param)
		buttons.append([text, param])
		param = 'transfer_receiver'
		text = 'Получатель перевода: ' + self.app.settings.get(param)
		buttons.append([text, param])
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите настройку', buttons, buttons, 2, 0)

	def show_setting(self, name):
		self.chat.set_context(self.address, 3)
		self.name = name
		text = f'Текущее значение: {self.app.settings.get(name)}\nВведите новое значение'
		self.GUI.tell(text)

	def show_confirmation(self):
		buttons = [['Подтвердить', 'confirm'], 'Отменить']
		self.GUI.tell_buttons('Подтвердите изменение параметра', buttons, buttons, 4, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		if self.message.btn_data == 'Назад':
			self.app.chat.user.admin.show_top_menu()
		elif self.message.btn_data == 'money':
			self.show_settings_money()

	def process_settings_money(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		else:
			self.show_setting(self.message.btn_data)

	def process_setting(self):
		self.value = self.message.text
		self.show_confirmation()

	def process_confirmation(self):
		if self.message.btn_data == 'confirm':
			self.app.settings.set(self.name, self.value)
			self.name = ''
			self.value = ''
		self.show_settings_money()

		