import sys
from datetime import datetime
import time
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui

class Sketch_item:
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
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_top_menu()
			elif message.function == '2':
				self.process_quantity()
			elif message.function == '3':
				self.process_quality()
			elif message.function == '4':
				self.process_name()
			elif message.function == '5':
				self.process_comment()
			elif message.function == '6':
				self.process_confirmation()

		if message.type == 'text' or self.message.type == 'document':
			self.GUI.messages_append(message)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.set_context(self.address, 1)
		if self.order.type == 'sketch':
			text = 'Загрузите ваши чертежи. Один или несколько файлов.'
		elif self.order.type == 'item':
			text = 'Сделайте несколько фотографий предмета и загрузите их.\n\n'
			text += 'Рекомендации к фото:\n'
			text += '1) перед фотографированием протрите линзу камеры сухой и чистой тканью,\n'
			text += '2) убедитесь что предмет находится в фокусе,\n'
			text += '3) если есть возможность сфотографируйте предмет на фоне линейки либо руки (чтобы видеть примерные габариты)\n'
			text += '3) сфотографируйте все особенности предмета.\n\n'
			text += 'Если есть возможность также сфотографируйте места крепления предмета к другим предметам.'
		if self.order.sketches:
			buttons = [['Загрузку закончил', 'uploaded']]
			self.GUI.tell_buttons(text, buttons, [], 1, self.order.id)
		else:
			self.GUI.tell(text)

	def show_quantity(self):
		text = 'Сколько экземпляров вам нужно?'
		buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
		self.GUI.tell_buttons(text, buttons, ['1', '2'], 2, self.order.id)

	def show_quality(self):
		text = 'Какое качество печати вам нужно? В зависимости от особенностей модели разница в стоимости печати может достигать 2.5 раза (для максимальной прочности).'
		buttons = [['максимально дешевое', 'cheap'], ['оптимальное цена/качество','optimal'], ['максимальное качество', 'quality'], ['максимальная прочность', 'durability']]
		self.GUI.tell_buttons(text, buttons, [], 3, self.order.id)

	def show_name(self):
		self.chat.set_context(self.address, 4)
		self.GUI.tell('Напишите название для вашего заказа')

	def show_comment(self):
		self.chat.set_context(self.address, 5)
		buttons = [['Комментариев к заказу не имею', 'none']]
		self.GUI.tell_buttons('Напишите комментарий', buttons, [], 5, self.order.id)

	def show_confirmation(self):
		text = 'Подтвердите создание заказа'
		buttons = [['Подтверждаю', 'confirm'], ['Удалить заказ', 'remove']]
		self.GUI.tell_buttons(text, buttons, buttons, 6, self.order.id)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.chat.context = ''
		file_id = self.message.file_id
		type_ = self.message.type
		if self.message.btn_data == 'uploaded':
			self.show_quantity()
			return
		elif type_ == 'photo' or (self.order.type == 'sketch' and type_ == 'document'):
			if file_id:
				self.order.sketches.append([file_id, type_])
		self.show_top_menu()

	def process_quantity(self):
		try:
			self.order.quantity = int(self.message.btn_data)
			self.show_quality()
		except:
			self.show_quantity()

	def process_quality(self):
		if self.message.btn_data == '':
			self.show_quality()
		self.order.quality = self.message.btn_data
		self.show_name()

	def process_name(self):
		self.chat.context = ''
		self.order.name = self.message.text
		self.show_comment()

	def process_comment(self):
		self.chat.context = ''
		if self.message.btn_data != 'none':
			self.order.comment = self.message.text
		self.show_confirmation()

	def process_confirmation(self):
		data = self.message.btn_data
		if data == 'confirm':
			self.order.date = datetime.today()
			self.order.logical_status = 'validate'
			self.order.user_id = self.app.chat.user_id
			self.app.orders_append(self.order)
			self.app.db.create_order(self.order)
			self.chat.user.show_wait_for_designer()
			# for chat in self.app.chats:
			# 	if chat.is_employee and 'Дизайнер' in chat.user.roles:
			# 		chat.user.designer.sketch_item.show_new_order(self.order)
		self.chat.user.reset_order()
		self.chat.user.show_top_menu()