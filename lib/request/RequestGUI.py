import sys
sys.path.append('../lib')
from lib.Gui import Gui

class RequestGUI:
	address = ''

	app = None
	chat = None
	GUI = None
	request = None
	# request_logic = None
	
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)
		# self.request_logic = app.request_logic

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
				self.process_request()
			elif message.function == '3':
				self.process_reply()
		if message.type == 'text':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		if len(self.app.requests) > 0:
			text = 'Все обращения:'
		else:
			text = 'Обращения отсутствуют'
		buttons = []
		for request in self.app.requests:
			buttons.append([request.text[:30], request.id])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_new_request(self, text):
		text = 'Новое обращение в службу поддержки:\n\n' + text
		self.GUI.tell(text)

	def show_request(self):
		text = self.request.text
		buttons = [['Ответить','reply']]
		buttons.append(['Перенести разговор в чат поддержки','chat'])
		buttons.append(['Оставить без ответа','ignore'])
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_reply(self):
		self.chat.set_context(self.address, 3)
		text = 'Напишите ответ на запрос:\n\n' + self.request.text
		buttons = ['Назад']
		self.GUI.tell_buttons(text, buttons, buttons, 3, 0)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.app.chat.user.admin.show_top_menu()
		else:
			for request in self.app.requests:
				if request.id == int(data):
					self.request = request
					self.show_request()

	def process_request(self):
		data = self.message.btn_data
		if data == 'reply':
			self.show_reply()
			return
		elif data == 'chat':
			self.send_chat()
			self.remove(self.request)
		elif data == 'ignore':
			self.remove(self.request)
		self.show_top_menu()

	def process_reply(self):
		if self.message.btn_data == 'Назад':
			self.chat.context = ''
		else:
			text = 'Ваш запрос:\n' + self.request.text
			text += '\n\nОтвет поддержки:\n' + self.message.text
			chat = self.app.get_chat(self.request.user_id)
			chat.user.info.show_support_reply(text)
			self.remove(self.request)
		self.show_top_menu()

#---------------------------- LOGIC ----------------------------

	def send_chat(self):
		chat = self.app.get_chat(self.request.user_id)
		chat.user.info.show_support_contact()

	def remove(self, request):
		self.app.request_logic.remove_request(self.request)
		self.app.db.remove_request(self.request)