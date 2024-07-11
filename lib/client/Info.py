from datetime import datetime, date, timedelta
import time
from lib.Gui import Gui
from lib.client.Color import Client_color

class Info:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.message = None
		self.address = address
		self.GUI = Gui(app, chat, address)

		self.client_color = Client_color(app, chat, address + '/1')

	def first_message(self, message):
		self.message = message
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				self.client_color.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
				elif function == '2':
					self.process_receive()
				elif function == '3':
					self.process_tech()
				elif function == '4':
					self.process_disclaimer()
				elif function == '5':
					self.process_request()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'Информация о студии'
		buttons = []
		buttons.append(['Доступные цвета и типы пластика', 'colors'])
		buttons.append(['Пункт выдачи, пересылка и сроки выполнения', 'receive'])
		buttons.append(['Технические подробности', 'tech'])
		# buttons.append(['Дисклеймер', 'disclaimer'])
		buttons.append(['Поддержка', 'request'])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_receive(self):
		start_date = self.app.order_logic.get_completion_date(0, '*')
		start_day = self.app.functions.russian_date(start_date)
		text = 'Пункт выдачи: г. Стерлитамак, ул. Сакко и Ванцетти, 63, "Бизнес-контакт". График работы: ежедневно с 9:00 до 21:00.\n\n'
		text += 'Доставка по странам СНГ службой boxberry за счет клиента.\n\n'
		text += 'Дата запуска заказа в печать с учетом текущей загруженности: ' + start_day
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_tech(self):
		text = 'Технология печати: одноцветная на fdm принтерах.\n\n'
		text += 'Используемые принтеры: BAMBU LAB P1S и CREALITY ENDER 3 S1 PRO.\n\n'
		text += 'Есть ограниченная возможность печатать поликарбонатом'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 3, 0)

	def show_disclaimer(self):
		text = """
Дисклеймер:
1) не даю гарантии на изделие
2) не несу ответственности за причиненный изделием вред
3) Если вес одного изделия превышает 0.8 кг, то могут быть отличия в цвете
3) Если общий вес нескольких изделий заказа превышает 0.8 кг, то также могут быть отличия в цвете"""
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 4, 0)

	def show_request(self):
		self.chat.set_context(self.address, 5)
		text = 'Опишите вашу проблему'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 5, 0)

	def show_support_contact(self, text):
		self.GUI.tell_permanent(text)

	def show_support_reply(self, text):
		self.GUI.tell_permanent(text)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.chat.user.last_data = ''
			self.chat.user.show_top_menu()
		elif data == 'colors':
			self.client_color.last_data = ''
			self.client_color.first_message(self.message)
		elif data == 'receive':
			self.show_receive()
		elif data == 'tech':
			self.show_tech()
		elif data == 'disclaimer':
			self.show_disclaimer()
		elif data == 'request':
			self.show_request()

	def process_receive(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_top_menu()

	def process_tech(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_top_menu()

	def process_disclaimer(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_top_menu()

	def process_request(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.chat.context = ''
		else:
			text = self.message.text
			chat = self.app.get_chats('Администратор')[0]
			request = self.app.request_logic.add_request(self.chat.user_id, text)
			chat.user.admin.requestGUI.show_new_request(request)
			self.GUI.tell('Ваш обращение получено, ожидайте ответа')
			time.sleep(2)
		self.show_top_menu()