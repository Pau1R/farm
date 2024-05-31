import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
from lib.client.Texts import Texts
import time

class Client_color:
	address = '1/2'
	
	app = None
	chat = None
	message = None
	order = None
	GUI = None
	texts = None
	colors = {}

	last_data = ''
	pending = False

	spool_logic = None
	color_logic = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(app)
		self.spool_logic = app.equipment.spool_logic
		self.color_logic = app.equipment.color_logic

	def first_message(self, message):
		self.message = message
		self.set_order()
		if self.order == None:
			self.show_colors()
		else:
			self.show_order_colors()

	def new_message(self, message):
		self.GUI.clear_chat()
		self.message = message
		self.set_order()
		self.GUI.clear_order_chat(message.instance_id)

		if message.data_special_format and (message.data == '' or message.data != self.last_data):	# process user button presses and skip repeated button presses
			self.last_data = message.data
			if message.function == '1':
				self.process_colors()
			elif message.function == '2':
				self.process_colors_ordered()
			elif message.function == '3':
				self.process_order_colors()
			elif message.function == '4':
				self.process_order_colors_ordered()
			elif message.function == '5':
				self.process_color()
			elif message.function == '6':
				self.process_booked()
		if message.type == 'text':
			self.GUI.messages_append(message)

	def set_order(self):
		order_id = int(self.message.instance_id)
		for order in self.app.orders:
			if order.order_id == order_id:
				self.order = order
				return
		self.order = None
		
#---------------------------- SHOW ----------------------------

	def show_colors(self):
		buttons = self.spool_logic.get_all_buttons('stock')
		types = self.app.settings.get('plastic_types').split(',')
		if self.spool_logic.is_ordered(types, 1, 1):
			buttons.append(['Ожидающие поставки', 'ordered'])
		buttons.append('Назад')
		self.GUI.tell_buttons('В наличии', buttons, buttons, 1, 0)

	def show_colors_ordered(self):
		buttons = self.spool_logic.get_all_buttons('ordered')
		buttons.append('Назад')
		self.GUI.tell_buttons('Цвета, ожидаемые к поставке', buttons, buttons, 2, 0)

	def show_order_colors(self):
		buttons = self.spool_logic.get_in_stock_buttons(self.order.plastic_type, self.order.color_id, self.order.weight, self.order.quantity)
		if self.spool_logic.is_ordered(self.order.plastic_type, self.order.weight, self.order.quantity):
			buttons.append(['Ожидающие поставки', 'ordered'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите цвет', buttons, buttons, 3, self.order.order_id)

	def show_order_colors_ordered(self):
		buttons = self.spool_logic.get_ordered_buttons(self.order.plastic_type, self.order.weight, self.order.quantity)
		if not buttons:
			self.show_order_colors()
		buttons.append('Назад')
		text = 'Цвета, ожидаемые к поставке'
		self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.order_id)

	def show_color(self, color_id, context_id):
		color = self.app.equipment.color_logic.get_color(self.message.btn_data)
		text = color.get_color_name()
		buttons = []
		order_id = 0
		if self.order != None:
			buttons.append(['Подтвердить выбор цвета', 'confirm^' + str(color.id) + '^' + str(context_id)])
			order_id = self.order.order_id
		buttons.append (['Назад', 'Назад^^' + str(context_id)])
		self.GUI.tell_photo_buttons(text, color.samplePhoto, buttons, buttons, 5, order_id)

	def show_booked(self):
		if self.order.is_free_start():
			text = 'Заказ принят и помещен в очередь на печать'
		else:
			text = 'Цвет забронирован. Если в течении 30 минут не будет внесена предоплата, бронь отменится'
		buttons = [['Хорошо','ok']]
		self.GUI.tell_buttons(text, buttons, buttons, 6, 0)

#---------------------------- PROCESS ----------------------------

	def process_colors(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.chat.user.last_data = ''
			self.chat.user.show_info()
		elif data == 'ordered':
			self.show_colors_ordered()
		else:
			self.show_color(data, 1)

	def process_colors_ordered(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_colors()
		else:
			self.show_color(data, 2)

	def process_order_colors(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.chat.user.client_order.last_data = ''
			self.chat.user.client_order.first_message(self.message)
		elif data == 'ordered':
			self.show_order_colors_ordered()
		else:
			self.show_color(data, 3)

	def process_order_colors_ordered(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_order_colors()
		else:
			self.show_color(data, 4)

	def process_color(self):
		data = self.message.btn_data
		context = int(data.split('^')[2])
		if data.split('^')[0] == 'Назад':
			if context == 1:
				self.show_colors()
			elif context == 2:
				self.show_colors_ordered()
			elif context == 3:
				self.show_order_colors()
			elif context == 4:
				self.show_order_colors_ordered()
		elif data.split('^')[0] == 'confirm':
			color_id = int(data.split('^')[1])
			if context == 3:
				if not self.order.reserve_plastic(['stock'], color_id):
					self.show_order_colors()
					return
			elif context == 4:
				if not self.order.reserve_plastic(['stock', 'ordered'], color_id):
					self.show_order_colors_ordered()
					return
			self.order.color_id = color_id
			self.order.set_price()
			self.app.db.update_order(self.order)
			self.show_booked()

	def process_booked(self):
		if self.message.btn_data == 'ok':
			self.chat.user.client_order.last_data = ''
			self.chat.user.client_order.first_message(self.message)