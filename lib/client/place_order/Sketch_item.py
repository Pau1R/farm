import sys
sys.path.append('../lib')
from lib.Gui import Gui
from lib.client.place_order.GUI.General import General_parameters

class Sketch_item:
	last_data = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.order = None
		self.address = address
		self.GUI = Gui(app, chat, address)
		self.general_parameters = General_parameters(app, chat, address + '/1')

	def first_message(self, message):
		self.order = self.chat.user.order
		self.order.sketches = []
		self.show_top_menu()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				self.general_parameters.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_top_menu()
		self.chat.add_if_text(self)

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.chat.set_context(self.address, 1)
		if self.order.type == 'sketch':
			text = 'Загрузите ваши чертежи. Один или несколько файлов или фото.'
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
			self.general_parameters.first_message(self.message)
			return
		elif type_ == 'photo' or (self.order.type == 'sketch' and type_ == 'document'):
			if file_id:
				self.order.sketches.append([file_id, type_])
		self.show_top_menu()