import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts

class Client_color:
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
		self.GUI = Gui(app, chat)
		self.texts = Texts(app)

	def first_message(self, message):
		order_id = int(message.data.split(",")[1])
		self.order = self.get_order(order_id)

		self.context = 'first_message'
		self.new_message(message)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.GUI.clear_order_chat(message.order_id)
		self.GUI.messages_append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_colors()
		elif context == 'colors':
			self.process_colors()
		elif context == 'color':
			self.process_color()
		
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
			buttons.append([color, str(self.message.order_id) + ',order_color,' + color])

		text = self.texts.price_text(int(self.message.order_id))
		text += '\n\nВыберите цвет'
		message = self.GUI.tell_buttons(text, buttons, buttons)
		message.general_clear = False
		message.order_id = self.message.order_id

	def show_color(self):
		self.context = 'color'
		buttons = [['Подтверждаю выбор цвета', str(self.message.order_id) + ',order_color,yes']]
		buttons.append (['Назад', str(self.message.order_id) + ',order_color,no'])
		self.GUI.tell_photo_buttons(self.color.name, self.color.samplePhoto, buttons, buttons)

		# бронь пластика на 20 минут при нажатии на кнопку цвета. Снятие брони при отображении списка цветов и при отказе от предоплаты. Если предоплата выполнена, бронь остается

#---------------------------- PROCESS ----------------------------

	def process_colors(self):
		self.context = ''
		name = self.message.data.split(",")[2]
		for color in self.app.equipment.colors:
			if color.name == name:
				self.color = color
				self.show_color()
				return
		self.color = ''
		self.show_colors()

	def process_color(self):
		self.context = ''
		if self.message.data.split(",")[2] == 'yes':
			self.chat.user.show_price(int(self.message.data.split(",")[0]))
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