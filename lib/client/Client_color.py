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

	spool_logic = None

	def __init__(self, app, chat):
		self.app = app
		self.chat = chat
		self.GUI = Gui(app, chat, self.address)
		self.texts = Texts(app)
		self.spool_logic = app.equipment.spool_logic

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
		if self.spool_logic.is_ordered():
			buttons.append(['Ожидающие поставки', 'ordered'])
		buttons.append('Назад')
		self.GUI.tell_buttons('В наличии', buttons, buttons, 1, 0)


		# filament = self.get_filament('stock', 'all', 0)
		# buttons = self.convert_to_buttons(filament, 'long', False, 0)
		# if self.get_filament('ordered', 'all', 0) != {}:
		# 	buttons.append(['Ожидающие поставки', 'ordered'])
		# buttons.append('Назад')
		# text = 'В наличии'
		# self.GUI.tell_buttons(text, buttons, buttons, 1, 0)

	def show_colors_ordered(self):
		buttons = self.spool_logic.get_all_buttons('ordered')
		buttons.append('Назад')
		self.GUI.tell_buttons('Цвета, ожидаемые к поставке', buttons, buttons, 2, 0)


		# filament = self.get_filament('ordered', 'all', 0)
		# buttons = self.convert_to_buttons(filament, 'long', True, 0)
		# buttons.append('Назад')
		# text = 'Цвета, ожидаемые к поставке'
		# self.GUI.tell_buttons(text, buttons, buttons, 2, 0)

	def show_order_colors(self):
		buttons = self.spool_logic.get_in_stock_buttons(self.order.plastic_type)
		if self.spool_logic.is_ordered(self.order.plastic_type):
			buttons.append(['Ожидающие поставки', 'ordered'])
		buttons.append('Назад')
		self.GUI.tell_buttons('Выберите цвет', buttons, buttons, 3, self.order.order_id)

		# filament = self.get_filament('stock', self.order.plastic_type, self.order.min_weight())
		# filament = self.trim_filament(filament, self.order)
		# ordered = self.get_filament('ordered', self.order.plastic_type, min_weight)
		# ordered = self.trim_filament(ordered, self.order)
		# buttons = self.convert_to_buttons(filament, 'short', False, min_weight)
		# if self.subtract_dictionaries(ordered, filament) != {}:
		# 	buttons.append(['Ожидающие поставки', 'ordered'])
		# buttons.append('Назад')
		# text = 'Выберите цвет'
		# self.GUI.tell_buttons(text, buttons, buttons, 3, self.order.order_id)

	def show_order_colors_ordered(self):
		buttons = self.spool_logic.get_ordered_buttons(self.order.plastic_type)
		buttons.append('Назад')
		text = 'Цвета, ожидаемые к поставке'
		self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.order_id)


		# ordered = self.get_filament('ordered', self.order.plastic_type, self.order.min_weight())
		# ordered = self.trim_filament(ordered, self.order)
		# stock = self.get_filament('stock', self.order.plastic_type, min_weight)
		# stock = self.trim_filament(stock, self.order)
		# ordered = self.subtract_dictionaries(ordered, stock)
		# buttons = self.convert_to_buttons(ordered, 'short', True, min_weight)
		# buttons.append('Назад')
		# text = 'Цвета, ожидаемые к поставке'
		# self.GUI.tell_buttons(text, buttons, buttons, 4, self.order.order_id)

	def show_color(self, color_id, context_id):
		color = self.get_color(self.message.btn_data)
		text = color.get_color_name()
		buttons = []
		order_id = 0
		if self.order != None:
			buttons.append(['Подтвердить выбор цвета', 'confirm^' + str(color.id) + '^' + str(context_id)])
			order_id = self.order.order_id
		buttons.append (['Назад', 'Назад^^' + str(context_id)])
		self.GUI.tell_photo_buttons(text, color.samplePhoto, buttons, buttons, 5, order_id)

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
				stock = self.get_filament('stock', self.order.plastic_type, self.order.min_weight())
				stock = self.trim_filament(stock, self.order)
				type_ = self.order.plastic_type
				if not (type_ in stock and color_id in stock.get(type_, {})):
					self.show_order_colors()
					return
			if context == 4:
				ordered = self.get_filament('ordered', self.order.plastic_type, self.order.min_weight())
				ordered = self.trim_filament(ordered, self.order)
				type_ = self.order.plastic_type
				if not (type_ in ordered and color_id in ordered.get(type_, {})):
					self.show_order_colors_ordered()
					return
			self.order.color_id = color_id
			self.order.reserve_plastic()
			self.order.set_price()
			self.app.db.update_order(self.order)
			self.chat.user.client_order.last_data = ''
			self.chat.user.client_order.first_message(self.message)

#---------------------------- LOGIC ----------------------------

	def get_order(self, order_id):
		for order in self.app.orders:
			if order.order_id == int(order_id):
				return order
		return None

	def get_color(self, id):
		colors = self.app.equipment.colors
		for color in colors:
			if color.id == int(id):
				return color

	def get_color_name(self, id):
		colors = self.app.equipment.colors
		for color in colors:
			if color.id == int(id):
				if color.parent_id == 0:
					return color.name
				else:
					for col in colors:
						if col.id == color.parent_id:
							return col.name + '-' + color.name.lower()

	def get_elem_from_list(self, lst):
		return lst[0]

	def get_filament(self, status, type, min_weight):
		filament = {}
		for spool in self.app.equipment.spools:
			# exclude by status:
			if spool.status != status:
				continue
			# exclude by type
			if type == 'any':
				types = self.app.settings.get('basic_plastic_types').split(',')
				if not spool.type in types:
					continue
			elif spool.type != type:
				if type != 'all':
					continue

			# add spool to dictionary
			if spool.type not in filament:
				filament[spool.type] = {spool.color_id: ''} # add spool type
			else:
				if spool.color_id not in filament[spool.type]: # add spool color
					col = filament[spool.type].copy()
					col.update({spool.color_id: ''})
			col = filament[spool.type]
			if spool.color_id in col:
				total_weight = col[spool.color_id]
				if total_weight == '':
					total_weight = 0
			if self.is_enough_weight(spool, min_weight):
				col.update({spool.color_id: total_weight + spool.weight}) # create or add spool weight
		filament = {key: {k: v for k, v in value.items() if v} for key, value in filament.items()} # remove empty values
		return filament  # {'PETG': {1: 998, 5: 4500, 7: 1000, 2: 1000}, 'PLA': {6: 9000}, 'PC': {1: 4000}, 'ABS': {6: 1000}, 'TPE': {9: 900}}

	def trim_filament(self, filament, order):
		weight = order.weight * order.quantity + 15
		type_ = [order.plastic_type]
		if type_[0] == 'any':
			type_ = self.app.settings.get('basic_plastic_types').split(',')
		for t in type_:
		    if t in filament:
		        filament[t] = {k: v for k, v in filament[t].items() if v > weight}
		return filament

	def convert_to_buttons(self, filament, name_format, include_date, min_weight):
		filament = filament.copy()
		buttons = []
		for type_ in filament:
			if type(filament[type_]) is dict:
				color_ids = filament[type_]
				for color_id in color_ids:
					if name_format == 'short':
						text = self.get_color_name(color_id)
					elif name_format == 'long':
						weight = int(color_ids[color_id])/1000 # convert weight to kg
						if int(weight) == weight: 			   # if weight is integer then remove decimal point
							weight = int(weight)
						text = f'{type_} {self.get_color_name(color_id)}: {str(weight)}кг'
					if include_date:
						for spool in self.app.equipment.spools:
							if spool.type == type_ and spool.color_id == color_id and self.is_enough_weight(spool, min_weight):
								date = self.app.functions.russian_date(spool.delivery_date_estimate)
								text += f' ({date})'
								break
					buttons.append([text, color_id])
		buttons.sort(key=self.get_elem_from_list)
		return buttons

	def is_enough_weight(self, spool, min_weight):
		weight = spool.weight - spool.used - spool.booked - 15  # remove 15 gramms from spool in case of weight accuracy error
		if weight > min_weight:
			return True

	def subtract_dictionaries(self, dict2, dict1):
		result = {}
		for key, subdict2 in dict2.items():
			if key not in dict1:
				result[key] = subdict2
			else:
				# Filter out keys present in dict1[key]
				filtered_subdict2 = {k: v for k, v in subdict2.items() if k not in dict1[key]}
				if filtered_subdict2:
					result[key] = filtered_subdict2
		return result