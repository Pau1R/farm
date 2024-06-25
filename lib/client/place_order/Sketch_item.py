import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.client.place_order.GUI.Values import Values

class Sketch_item:
	address = ''

	app = None
	chat = None
	order = None
	GUI = None

	last_data = ''

	values = None

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.values = Values(app, chat, address + '/1')

	def first_message(self, message):
		self.order = self.chat.user.order
		self.order.sketches = []
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		if message.data_special_format:
			if message.file3 == '' and (message.data == '' or message.data != self.last_data):
				self.last_data = message.data
				if message.function == '1':
					self.process_top_menu()
			elif message.file3 == '1':
				self.values.new_message(message)
		if message.type in ['text', 'document', 'photo']:
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
			text += '3) если есть возможность сфотографируйте предмет на фоне линейки либо руки (чтобы видеть примерные габариты),\n'
			text += '3) сфотографируйте все особенности предмета,\n'
			text += '4) если есть возможность также сфотографируйте места крепления предмета к другим предметам.'
		if self.order.sketches:
			text += f'\n\nЗагружено файлов: {len(self.order.sketches)}'
			buttons = [['Загрузку закончил', 'uploaded']]
			self.GUI.tell_buttons(text, buttons, [], 1, self.order.id)
		else:
			self.GUI.tell(text)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.chat.context = ''
		file_id = self.message.file_id
		type_ = self.message.type
		if self.message.btn_data == 'uploaded':
			self.values.first_message(self.message)
			return
		elif type_ == 'photo' or (self.order.type == 'sketch' and type_ == 'document'):
			if file_id:
				self.order.sketches.append([file_id, type_])
		self.show_top_menu()