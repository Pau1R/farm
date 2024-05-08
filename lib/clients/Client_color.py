import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.clients.Texts import Texts

class Client_color:
	app = None
	chat = None
	message = None
	order = None
	GUI = None
	texts = None

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
		self.GUI.messages.append(message)
		self.message = message
		context = self.context

		if context == 'first_message':
			self.show_colors()
		elif context == 'colors':
			self.process_colors()
		

#---------------------------- SHOW ----------------------------

	def show_colors(self):
		self.context = 'colors'
		buttons = []
		for spool in self.app.equipment.spools:
			if self.order.plastic_type == 'Любой' or (spool.type == self.order.plastic_type):
				if spool.weight - spool.booked - 15 > self.order.weight * self.order.quantity:
					buttons.append(spool.color)
		text = self.texts.price_text(self.message.order_id)
		text += f'\n\nВыберите цвет'
		self.GUI.tell_buttons(text, buttons, buttons)





		# - spools:
		# 	- тип
		# 	- цвет
		# 	- остаток
		# 	- бронь

		# для каждой spools где тип и (остаток-бронь)>(int(order.weight)*order.quantity+15грамм)
		# list of buttons
		# бронь пластика на 20 минут при нажатии на кнопку цвета. Снятие брони при отображении списка цветов и при отказе от предоплаты. Если предоплата выполнена, бронь остается

#---------------------------- PROCESS ----------------------------

	def process_colors(self):
		o = ''

#---------------------------- LOGIC ----------------------------

	def get_order(self, order_id):
		for order in self.app.orders:
			if order.order_id == order_id:
				return order
		return None