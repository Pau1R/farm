import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts

class Client_color:
	address = '1/2'
	
	app = None
	chat = None
	message = None
	order = None
	GUI = None
	context = ''
	texts = None
	color = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(app)

	def first_message(self, message):
		self.order = self.get_order(message.instance_id)
		self.show_colors()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.clear_order_chat(message.instance_id)
		self.message = message

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_colors()
			elif message.function == '2':
				self.process_color()
		if message.type == 'text':
			self.GUI.messages_append(message)
		
#---------------------------- SHOW ----------------------------

	def show_colors(self):
		self.context = 'colors'
		buttons = []
		colors = []
		for spool in self.app.equipment.spools:
			if self.order.plastic_type == 'Любой' or (spool.type == self.order.plastic_type):
				if spool.weight - spool.booked - 15 > self.order.weight * self.order.quantity:
					colors.append(spool.color)
		colors = list(dict.fromkeys(colors))
		for color in colors:
			buttons.append([color])

		text = self.texts.price_text(int(self.message.order_id))
		text += '\n\nВыберите цвет'
		message = self.GUI.tell_buttons(text, buttons, buttons, 1, self.order.order_id, 1, self.order.order_id)
		message.general_clear = False
		message.order_id = self.message.order_id

	def show_color(self):
		self.context = 'color'
		buttons = [['Подтверждаю выбор цвета', 'yes']]
		buttons.append ('Назад')
		self.GUI.tell_photo_buttons(self.color.name, self.color.samplePhoto, buttons, buttons, 2, self.order.order_id)

		# бронь пластика на 20 минут при нажатии на кнопку цвета. Снятие брони при отображении списка цветов и при отказе от предоплаты. Если предоплата выполнена, бронь остается

#---------------------------- PROCESS ----------------------------

	def process_colors(self):
		self.context = ''
		# name = self.message.data.split(",")[2]
		name = self.message.btn_data
		for color in self.app.equipment.colors:
			if color.name == name:
				self.color = color
				self.show_color()
				return
		self.color = ''
		self.show_colors()

	def process_color(self):
		self.context = ''
		if self.message.btn_data == 'yes':
		# if self.message.data.split(",")[2] == 'yes':
			self.chat.user.show_price(int(self.message.instance_id))
			# self.GUI.tell('Благодарим ')
			# move on to payment
		else:
			self.show_colors()

#---------------------------- LOGIC ----------------------------

	def get_order(self, order_id):
		for order in self.app.orders:
			if order.order_id == order_id:
				return order
		return None