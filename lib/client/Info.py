from lib.Gui import Gui
from lib.client.Client_color import Client_color

class Info:
	address = ''

	app = None
	chat = None
	message = None
	GUI = None
	client_color = None

	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)

		self.client_color = Client_color(app, chat, address + '/1')

	def first_message(self, message):
		self.message = message
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format:
			if message.file3 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.process_top_menu()
				elif message.function == '2':
					self.process_receive()
				elif message.function == '3':
					self.process_tech()
				elif message.function == '4':
					self.process_disclaimer()
				elif message.function == '5':
					self.process_support()
			elif message.file3 == '1':
				self.client_color.new_message(message)
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		text = 'Информация о студии'
		buttons = []
		buttons.append(['Доступные цвета и типы пластика', 'colors'])
		buttons.append(['Получение заказов', 'receive'])
		buttons.append(['Технические подробности', 'tech'])
		buttons.append(['Дисклеймер', 'disclaimer'])
		buttons.append(['Поддержка', 'support'])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_receive(self):
		text = 'Среднее время выполнения заказа: 2-3 дня\n\n'
		text += 'Пункт выдачи: г. Стерлитамак, ул. Сакко и Ванцетти, 63, "Бизнес-контакт". График работы: ежедневно с 9:00 до 21:00.\n\n'
		text += 'Доставка по странам СНГ службой boxberry за счет клиента'
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

	def show_support(self):
		self.chat.set_context(self.address, 5)
		text = 'Опишите вашу проблему'
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 5, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_top_menu()
		elif data == 'colors':
			self.client_color.last_data = ''
			self.client_color.first_message(self.message)
		elif data == 'receive':
			self.show_receive()
		elif data == 'tech':
			self.show_tech()
		elif data == 'disclaimer':
			self.show_disclaimer()
		elif data == 'support':
			self.show_support()

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

	def process_support(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.chat.context = ''
		else: # TODO: think over the support logic
			text = self.message.text
			self.GUI.tell('Ваш обращение получено, ждите ответа')
			time.sleep(2)
		self.show_top_menu()