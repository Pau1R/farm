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
	texts = None
	colors = {}

	last_data = ''
	pending = False

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(app)

	def first_message(self, message):
		self.message = message
		self.set_order()
		self.show_colors()

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
				self.process_color()
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
		order = self.order
		if order == None:
			text = 'Наличие'
			order_id = 0
			all_colors = True
		else:
			text = 'Выберите цвет'
			order_id = order.order_id
			all_colors = False

		# prepare all filament
		filament = {}
		for spool in self.app.equipment.spools:
			if self.pending and spool.status == 'stock':
				continue
			elif spool.status == 'pending':
				continue
			if spool.type not in filament:
				filament[spool.type] = {spool.color_id: ''} # add spool type
			else:
				if spool.color_id not in filament[spool.type]: # add spool color
					col = filament[spool.type].copy()
					col.update({spool.color_id: ''})
			col = filament[spool.type] # add spool weight
			if spool.color_id in col:
				total_weight = col[spool.color_id]
				if total_weight == '':
					total_weight = 0
			weight = spool.weight - spool.used - spool.booked
			if weight > 15:
				col.update({spool.color_id: total_weight + spool.weight})

		# convert filament to buttons
		buttons = []
		for type_ in filament:
			if type(filament[type_]) is dict:
				color_ids = filament[type_]
				for color_id in color_ids:
					# show all colors
					if all_colors:
						if color_ids[color_id] != '':
							weight = int(color_ids[color_id])/1000
							if int(weight) == weight:
								weight = int(weight)
							txt = f'{type_} {self.get_color_name(color_id)}: {str(weight)}кг'
							buttons.append([txt, color_id])
					# show colors available for order
					else:
						if order.plastic_type == 'Любой' or (type_ == order.plastic_type):
							for color in self.app.equipment.colors:
								if color.id == color_id:
									buttons.append([self.get_color_name(color.id), color.id])
									break
		# if not all_colors:
		# 	buttons = list(dict.fromkeys(buttons))
		buttons.sort(key=self.get_elem_from_list)

		activate = False
		for spool in self.app.equipment.spools:
			if spool.status == 'ordered':
				if all_colors:
					activate = True
				elif order.plastic_type == 'Любой' or (spool.type == order.plastic_type): # process limited spool types
					activate = True
		if not self.pending and activate:
			buttons.append(['Ожидающие поставки', 'pending'])
		# buttons.append(['Хочу другой цвет', 'other_color']) # TODO: make it possible to preorder plastic of specific color
		buttons.append('Назад')
		self.GUI.tell_buttons(text, buttons, buttons, 1, order_id)

	def show_color(self):
		color = None
		for color_ in self.app.equipment.colors:
			if color_.id == int(self.message.btn_data):
				color = color_
				break
		buttons = []
		if self.order == None:
			order_id = 0
		else:
			buttons.append(['Подтвердить выбор цвета', 'confirm^' + str(color.id)])
			order_id = self.message.instance_id
		buttons.append ('Назад')
		if color.parent_id == 0:
			name = color.name
		else:
			for col in self.app.equipment.colors:
				if col.id == color.parent_id:
					name = col.name + '-' + color.name.lower()
		self.GUI.tell_photo_buttons(name, color.samplePhoto, buttons, buttons, 2, order_id)

#---------------------------- PROCESS ----------------------------

	def process_colors(self):
		data = self.message.btn_data
		if data == 'Назад':
			if self.pending:
				self.pending = False
				self.show_colors()
			elif self.order == None:
				self.chat.user.last_data = ''
				self.chat.user.show_info()
			else:
				self.chat.user.client_order.last_data = ''
				self.chat.user.client_order.first_message(self.message)
			self.last_data = ''
		elif data == 'pending':
			self.pending = True
			self.show_colors()
			# self.show_ordered()
		elif data == 'other_color':
			self.show_other_color()
		else:
			self.show_color()

	def process_color(self):
		data = self.message.btn_data
		if data == 'Назад':
			self.show_colors()
		elif data.split('^')[0] == 'confirm':
			color_id = int(data.split('^')[1])
			# TODO: if color just disappeared: self.show_colors()
			# TODO: бронь пластика на 20 минут при нажатии на кнопку цвета. Снятие брони при отображении списка цветов и при отказе от предоплаты. Если предоплата выполнена, бронь остается
			self.order.color_id = color_id
			self.order.set_price()
			self.app.db.update_order(self.order)
			self.chat.user.client_order.last_data = ''
			self.chat.user.client_order.first_message(self.message)

#---------------------------- LOGIC ----------------------------

	def get_order(self, order_id):
		for order in self.app.orders:
			if order.order_id == order_id:
				return order
		return None

	def get_color_name(self, id):
		colors = self.app.equipment.colors
		for color in colors:
			if color.id == int(id):
				if color.parent_id == 0:
					return color.name
				else:
					for col in colors:
						if col.id == color.parent_id:
							return col.name + '-' + color.name

	def get_elem_from_list(self, lst):
		return lst[0]