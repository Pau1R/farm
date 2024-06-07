import sys
from datetime import datetime
import time
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Their_item:
	address = ''

	app = None
	chat = None
	order = None
	GUI = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, self.address)

	def first_message(self, message):
		self.order = self.chat.user.order
		self.show_name()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_name()
			elif message.function == '2':
				self.process_photos()
			elif message.function == '3':
				self.process_quantity()
			elif message.function == '4':
				self.process_comment()
			elif message.function == '5':
				self.process_confirmation()

		if message.type == 'text' or self.message.type == 'document':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_name(self):
		self.chat.set_context(self.address, 1)
		text = 'Для создания копии вашего предмета нужно сделать следующее:\n'
		text += '1) Отправить фотографии предмета\n'
		text += '2) Дождаться результа предварительной оценки\n'
		text += '3) Если оценка вас устраивает то привезти предмет в пункт выдачи в центре Стерлитамака\n\n'
		text += 'Предварительная оценка не учитывает стоимость печати. Как правило, стоимость печати значительно дешевле стоимости моделирования.\n\n'
		text += 'Для продолжения напишите название вашего заказа'
		self.GUI.tell(text)

	def show_photos(self):
		self.chat.set_context(self.address, 2)
		text = 'Сфотографируйте предмет со всех сторон и загрузите фото.\n\n'
		text += 'Требования к фото:\n'
		text += '1) предмет должен быть в фокусе\n'
		text += '2) фотографии должно быть не размыты, перед фотографированием протрите линзу камеры\n'
		text += '3) на фотографиях должны быть видны все особенности предмета\n\n'
		text += 'Если есть возможность также сфотографируйте места крепления предмета к другим предметам'
		if self.order.sketches:
			buttons = [['Загрузку закончил', 'uploaded']]
			self.GUI.tell_buttons(text, buttons, [], 2, self.order.id)
		else:
			self.GUI.tell(text)
	
	def show_quantity(self):
		text = 'Сколько экземпляров вам нужно?'
		buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
		self.GUI.tell_buttons(text, buttons, ['1', '2'], 3, self.order.id)

	def show_comment(self):
		self.chat.set_context(self.address, 4)
		buttons = ['Комментариев к заказу не имею']
		self.GUI.tell_buttons('Напишите комментарий', buttons, [], 4, self.order.id)

	def show_confirmation(self):
		text = 'Подтвердите создание заказа'
		buttons = [['Подтверждаю', 'confirm'], ['Удалить заказ', 'remove']]
		self.GUI.tell_buttons(text, buttons, buttons, 5, self.order.id)

#---------------------------- PROCESS ----------------------------

	def process_name(self):
		self.order.name = self.message.text
		self.show_photos()

	def process_photos(self):
		self.chat.context = ''
		if self.message.btn_data == 'uploaded':
			self.show_quantity()
		else:
			file_id = self.message.file_id
			type_ = self.message.type
			if type_ in ['document', 'photo'] and file_id:
				self.order.sketches.append([file_id, type_])
			self.show_photos()

	def process_quantity(self):
		try:
			self.order.quantity = int(self.message.btn_data)
			self.show_comment()
		except:
			self.show_quantity()	

	def process_comment(self):
		self.chat.context = ''
		if self.message.btn_data != 'Комментариев к заказу не имею':
			self.order.comment = self.message.text
		self.show_confirmation()

	def process_confirmation(self):
		data = self.message.btn_data
		if data == 'confirm':
			self.order.date = datetime.today()
			self.order.print_status = 'preparing'
			self.order.status = 'validate'
			self.order.user_id = self.app.chat.user_id
			self.app.orders_append(self.order)
			self.app.db.create_order(self.order)
			self.chat.user.show_wait_for_designer()
			for chat in self.app.chats:
				if chat.is_employee and 'Дизайнер' in chat.user.roles:
					chat.user.designer.validate.show_new_order(self.order)
		self.chat.user.reset_order()
		self.chat.user.show_top_menu()