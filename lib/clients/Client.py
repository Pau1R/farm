import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.clients.Texts import Texts
from lib.clients.Order import Order
from lib.clients.Client_model import Client_model
from lib.clients.Client_color import Client_color

class Client:
	app = None
	chat = None
	order = None
	name = ''
	date = None
	GUI = None
	context = ''
	message = None
	texts = None
	
	menu = None
	client_model = None
	client_color = None
	order_id = None

	payId = ''
	balance = 0.0

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.texts = Texts(app)
		self.GUI = Gui(app, chat)

		self.order = Order(app, 1)
		self.client_model = Client_model(app, chat)
		self.client_color = Client_color(app, chat)

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		context = self.context

		if message.text == '/start':
			self.order.reset()
			self.menu = None
			self.show_top_menu()
		elif self.menu == self.client_model:
			self.menu.new_message(message)
		elif self.menu == self.client_color:
			self.menu.new_message(message)
		else:
			self.GUI.messages.append(message)
			if context == 'top_menu':
				self.process_top_menu()
			if context == 'supports':
				self.process_supports()
			if context == 'price':
				self.process_price()

#---------------------------- SHOW ----------------------------

	def show_top_menu(self):
		self.context = 'top_menu'
		self.GUI.tell_buttons(self.texts.top_menu, self.texts.top_menu_buttons.copy(), [])
		# TODO: add functionality

	def show_supports(self, order_id):
		self.context = 'supports'
		order = self.get_order(order_id)
		self.GUI.tell_permanent(f'Оценка вашей модели "{order.name}" завершена.')
		if order.support_time > 0:
			text = self.texts.price_text(order_id)
			text += '\n\nВы хотите убрать поддержки самостоятельно?'
			message = self.GUI.tell_buttons(text, self.texts.supports_btns(order_id), [])
			message.general_clear = False
			message.order_id = order_id
		else:
			self.goto_color(order_id)

	def show_price(self, order_id):
		self.context = 'price'
		self.GUI.tell_buttons(self.texts.price_text(order_id), self.texts.price_btns.copy(), [])

	def show_rejected(self, order_id, reason):
		my_order = self.get_order(order_id)
		self.GUI.tell(f'Ваша модель {my_order.name} не прошла проверку\nПричина: {reason}')
		self.app.db.remove_order(my_order)
		self.app.orders.remove(my_order)

#---------------------------- PROCESS ----------------------------

	def process_top_menu(self):
		self.context = ''
		if self.message.text == 'я_хочу_стать_сотрудником':
			self.chat.get_employed = True
			self.GUI.tell('Ждите подтверждения')
		elif self.message.data == 'farm model':
			self.GUI.tell('Здесь будут находится готовые модели')
		elif self.message.data == 'user model':
			self.menu = self.client_model
			self.client_model.first_message(self.message)
		elif self.message.data == 'user drawing':
			self.GUI.tell('Здесь вы можете загрузить свои чертежы или рисунки для создания по ним 3д модели.')

	def process_supports(self):
		self.context = ''
		order_id = int(self.message.data.split(",")[1])
		self.GUI.clear_order_chat(order_id)
		my_order = self.get_order(order_id)
		if self.message.data.split(",")[0] == 'клиент':
			my_order.support_remover = self.message.data
		elif self.message.data.split(",")[0] == 'продавец':
			my_order.support_remover = self.message.data.split(",")[0]
			my_order.price += int(my_order.support_time * my_order.quantity * self.app.support_remove_price)
		else:
			self.show_supports(order_id)
			return
		self.goto_color(order_id)

	def process_price(self):
		i = ''

#---------------------------- LOGIC ----------------------------

	def goto_color(self, order_id):
		self.menu = self.client_color
		self.message.order_id = order_id
		self.client_color.first_message(self.message)

	def get_order(self, order_id):
		for order in self.app.orders:
			if order.order_id == order_id:
				return order
		return None

# TODO:
# - client color selection
# - client process prepayment