import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts

class Client_model:
	app = None
	chat = None
	order = None
	GUI = None
	texts = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat)
		self.texts = Texts(app)

	def first_message(self, message):
		self.order = self.chat.user.order
		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.messages_append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			# self.show_name()
			self.process_file()
		elif context == 'name':
			self.process_name()
		elif context == 'quantity':
			self.process_quantity()
		elif context == 'conditions':
			self.process_conditions()
		elif context == 'comment':
			self.process_comment()
		elif context == 'file':
			self.process_file()

#---------------------------- SHOW ----------------------------

	def show_name(self):
		self.context = 'name'
		self.GUI.tell(self.texts.model_name)

	def show_quantity(self):
		self.context = 'quantity'
		self.GUI.tell_buttons(self.texts.model_quantity, self.texts.model_quantity_buttons.copy(), ['1', '2'])

	def show_conditions(self):
		self.context = 'conditions'
		self.GUI.tell_buttons(self.texts.model_conditions, self.texts.model_conditions_buttons.copy(), [])

	def show_comment(self):
		self.context = 'comment'
		self.GUI.tell_buttons(self.texts.model_comment, ['Комментариев к заказу не имею'], [])

	def show_file(self):
		self.context = 'file'
		self.GUI.tell(self.texts.file)

	def show_extention_error(self):
		self.GUI.tell('Неверный формат файла')
		self.show_file()

	def show_wait_for_designer(self):
		self.context = 'wait_for_designer'
		self.GUI.tell(self.texts.wait_for_designer)

#---------------------------- PROCESS ----------------------------

	def process_name(self):
		self.context = ''
		self.order.name = self.message.text
		self.show_quantity()

	def process_quantity(self):
		self.context = ''
		try:
			self.order.quantity = int(self.message.data)
			self.show_conditions()
		except:
			self.show_quantity()

	def process_conditions(self):
		self.context = ''
		if self.message.data == '':
			self.show_conditions()
		self.order.conditions = self.message.data
		self.show_comment()

	def process_comment(self):
		self.context = ''
		if self.message.data != 'Комментариев к заказу не имею':
			self.order.comment = self.message.text
		self.show_file()

	def process_file(self):
		self.context = ''

		self.message.file_name = 'hi.stl'
		self.message.file_id = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'
		self.message.type = 'document'
		self.order.name = 'название модели'
		self.order.conditions = 'В доме'
		self.order.quantity = 3

		if self.message.type == 'document':
			extention = self.message.file_name.split(".")[-1]
			if extention in self.texts.supported_3d_extensions:
				self.order.status = 'validate'
				self.order.user_id = self.app.chat.user_id
				self.order.model_file = self.message.file_id
				self.order.tell_designer()
				self.app.orders.append(self.order)
				self.app.db.create_order(self.order)
				self.show_wait_for_designer()
				return
		self.show_extention_error()
		
		# self.GUI.tell_document('BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ', 'this is caption text')


		# move on to selecting current settings
		# generate buttons of available colors