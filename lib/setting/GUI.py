import sys
sys.path.append('../lib')
from lib.Gui import Gui

class SettingsGUI:
	address = ''

	app = None
	chat = None
	GUI = None

	last_data = ''

	name = ''
	value = ''

	context = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)

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
					self.process_settings()
				elif function == '3':
					self.process_setting()
				elif function == '4':
					self.process_confirmation()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		buttons = [['Финансы', 'money'], ['Другие настройки', 'plastic_types'], 'Назад']
		self.GUI.tell_buttons('Выберите категорию', buttons, ['Назад'], 1, 0)

	def show_settings_money(self):
		self.context = 'settings_money'
		buttons = []
		param = 'support_remove_price'
		text = 'Стоимость одной минуты удаления поддержек: ' + self.app.setting.get(param) + ' рублей'
		buttons.append([text, param])
		param = 'prepayment_percent'
		text = 'Процент предоплаты: ' + self.app.setting.get(param) + '%'
		buttons.append([text, param])
		param = 'prepayment_free_max'
		text = 'Максимальная сумма без предоплаты: ' + self.app.setting.get(param) + ' рублей'
		buttons.append([text, param])
		param = 'phone_number'
		text = 'Телефон для переводов: ' + self.app.setting.get(param)
		buttons.append([text, param])
		param = 'card_number'
		text = 'Карточка для переводов: ' + self.app.setting.get(param)
		buttons.append([text, param])
		param = 'account_number'
		text = 'Счет для переводов: ' + self.app.setting.get(param)
		buttons.append([text, param])
		param = 'transfer_receiver'
		text = 'Получатель перевода: ' + self.app.setting.get(param)
		buttons.append([text, param])
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите настройку', buttons, buttons, 2, 0)

	def show_settings_other(self):
		self.context = 'settings_other'
		buttons = []
		param = 'plastic_types'
		text = 'Используемые типы материалов: ' + self.app.setting.get(param)
		buttons.append([text, param])
		param = 'basic_plastic_types'
		text = 'Базовые типы материалов (последовательность указывает очередность назначения): ' + self.app.setting.get(param)
		buttons.append([text, param])
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите настройку', buttons, buttons, 2, 0)

	def show_setting(self, name):
		self.chat.set_context(self.address, 3)
		self.name = name
		text = f'Текущее значение: {self.app.setting.get(name)}\nВведите новое значение'
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
		elif self.message.btn_data == 'plastic_types':
			self.show_settings_other()

	def process_settings(self):
		if self.message.btn_data == 'Назад':
			self.show_top_menu()
		else:
			self.show_setting(self.message.btn_data)

	def process_setting(self):
		self.value = self.message.text
		self.show_confirmation()

	def process_confirmation(self):
		if self.message.btn_data == 'confirm':
			self.app.setting.set(self.name, self.value)
			self.name = ''
			self.value = ''
		if self.context == 'settings_money':
			self.show_settings_money()
		elif self.context == 'settings_other':
			self.show_settings_other()

		