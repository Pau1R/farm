import sys
sys.path.append('../lib')
from lib.Msg import Message
from lib.Gui import Gui
import time

class Client_color:
	colors = {}

	last_data = ''
	pending = False

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.message = None
		self.order = None
		self.address = address
		self.GUI = Gui(app, chat, self.address)
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

		file = self.chat.next_level_id(self)
		function = message.function
		if message.data_special_format:
			if file == '1':
				self.general_parameters.new_message(message)
			elif self.chat.not_repeated_button(self):
				if function == '1':
					self.process_colors()
				elif function == '2':
					self.process_colors_ordered()
				elif function == '3':
					self.process_order_colors()
				elif function == '4':
					self.process_order_colors_ordered()
				elif function == '5':
					self.process_color()
				elif function == '6':
					self.process_booked()
		self.chat.add_if_text(self)

	def set_order(self):
		order_id = int(self.message.instance_id)
		for order in self.app.orders:
			if order.id == order_id:
				self.order = order
				return
		self.order = None
		
#---------------------------- SHOW ----------------------------

	def show_colors(self):
		buttons = self.spool_logic.get_all_buttons('stock')
		types = self.app.setting.get('plastic_types').split(',')
		if self.spool_logic.is_ordered(types, 1, 1):
			buttons.append(['Ожидающие поставки', 'ordered'])
		buttons.append('Назад')
		self.GUI.tell_buttons('В наличии', buttons, buttons, 1, 0)

	def show_colors_ordered(self):
		buttons = self.spool_logic.get_all_buttons('ordered')
		buttons.append('Назад')
		self.GUI.tell_buttons('Ожидающие поставки', buttons, buttons, 2, 0)

	def show_order_colors(self):
		buttons = self.spool_logic.get_in_stock_buttons(self.order.plastic_type, self.order.weight, self.order.quantity)
		if self.spool_logic.is_ordered(self.order.plastic_type, self.order.weight, self.order.quantity):
			buttons.append(['Ожидающие поставки', 'ordered'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите цвет', buttons, buttons, 3, self.order.id)

	def show_order_colors_ordered(self):
		buttons = self.spool_logic.get_ordered_buttons(self.order.plastic_type, self.order.weight, self.order.quantity)
		if not buttons:
			self.show_order_colors()
		buttons.append('Назад')
		text = 'Ожидающие поставки'
		self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.id)

	def show_color(self, color_id, context_id):
		color = self.app.equipment.color_logic.get_color(int(self.message.btn_data))
		text = color.get_name()
		buttons = []
		order_id = 0
		if self.order != None:
			buttons.append(['Подтвердить выбор цвета', 'confirm^' + str(color.id) + '^' + str(context_id)])
			order_id = self.order.id
		buttons.append (['Назад', 'Назад^^' + str(context_id)])
		self.GUI.tell_photo_buttons(text, color.samplePhoto, buttons, buttons, 5, order_id)

	def show_booked(self):
		text = 'Цвет забронирован. Если в течении 30 минут не будет внесена предоплата, бронь отменится'
		buttons = [['Согласен','ok']]
		self.GUI.tell_buttons(text, buttons, buttons, 6, 0)

#---------------------------- PROCESS ----------------------------

	def process_colors(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.chat.user.info.last_data = ''
			self.chat.user.info.show_top_menu()
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
			self.chat.user.order_GUI.last_data = ''
			self.chat.user.order_GUI.first_message(self.message)
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
			self.order.logical_status = 'parameters_set'
			self.order.set_price()
			self.app.db.update_order(self.order)
			self.show_booked()

	def process_booked(self):
		if self.message.btn_data == 'ok':
			self.chat.user.order_GUI.last_data = ''
			self.chat.user.order_GUI.first_message(self.message)