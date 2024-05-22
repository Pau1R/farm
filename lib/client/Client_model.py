import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts
import time

class Client_model:
	address = '1/1'

	app = None
	chat = None
	order = None
	GUI = None
	texts = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(app)

	def first_message(self, message):
		self.order = self.chat.user.order

		self.show_name()
		# self.process_file()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_name()
			elif message.function == '2':
				self.process_quantity()
			elif message.function == '3':
				self.process_conditions()
			elif message.function == '4':
				self.process_comment()
			elif message.function == '5':
				self.process_file()
		if message.type == 'text' or self.message.type == 'document':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_name(self):
		self.chat.set_context(self.address, 1)
		self.GUI.tell(self.texts.model_name)

	def show_quantity(self):
		text = self.texts.model_quantity
		buttons = self.texts.model_quantity_buttons.copy()
		self.GUI.tell_buttons(text, buttons, ['1', '2'], 2, self.order.order_id)

	def show_conditions(self):
		text = self.texts.model_conditions
		buttons = self.texts.model_conditions_buttons.copy()
		self.GUI.tell_buttons(text, buttons, [], 3, self.order.order_id)

	def show_comment(self):
		# TODO: create posibility to input both text and buttons
		text = self.texts.model_comment
		buttons = ['Комментариев к заказу не имею']
		self.GUI.tell_buttons(text, buttons, [], 4, self.order.order_id)

	def show_file(self):
		self.chat.set_context(self.address, 5)
		self.GUI.tell(self.texts.file)

	def show_extention_error(self):
		self.GUI.tell('Неверный формат файла')
		self.show_file()

	def show_wait_for_designer(self):
		self.GUI.tell_permanent(f'Заказ {self.order.name} передан дизайнеру для оценки, ожидайте.')
		time.sleep(3)
		self.chat.user.show_top_menu()

#---------------------------- PROCESS ----------------------------

	def process_name(self):
		self.order.name = self.message.text
		self.show_quantity()

	def process_quantity(self):
		try:
			self.order.quantity = int(self.message.btn_data)
			self.show_conditions()
		except:
			self.show_quantity()

	def process_conditions(self):
		if self.message.btn_data == '':
			self.show_conditions()
		self.order.conditions = self.message.btn_data
		self.show_comment()

	def process_comment(self):
		if self.message.btn_data != 'Комментариев к заказу не имею':
			self.order.comment = self.message.text
		self.show_file()

	def process_file(self):

		# self.message.file_name = 'hi.stl'
		# self.message.file_id = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'
		# self.message.type = 'document'
		# self.order.name = 'название модели'
		# self.order.conditions = 'В доме'
		# self.order.quantity = 3

		if self.message.type == 'document':
			extention = self.message.file_name.split(".")[-1]
			if extention in self.texts.supported_3d_extensions:
				self.order.status = 'validate'
				self.order.user_id = self.app.chat.user_id
				self.order.model_file = self.message.file_id
				# self.order.tell_designer()
				self.app.orders.append(self.order)
				self.app.db.create_order(self.order)
				self.show_wait_for_designer()
				for chat in self.app.chats:
					if chat.is_employee and 'Дизайнер' in chat.user.roles:
						chat.user.designer.validate.show_new_order(self.order)
				return
		self.show_extention_error()
		
		# self.GUI.tell_document('BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ', 'this is caption text')