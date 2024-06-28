from datetime import date

class Spool_logic:
	app = None
	spools = []
	color_logic = None

	def __init__(self, app):
		self.app = app
		self.spools = app.equipment.spools
		self.color_logic = self.app.equipment.color_logic

	def available_spools(self): # get all spools, return format: {type: {color_id: total_weight, ...}, ...}
		spools = {}
		for spool in self.spools:
			if spool.type not in spools:
				spools[spool.type] = {}  # add spool type
			if spool.color_id not in spools[spool.type]:
				spools[spool.type][spool.color_id] = 0  # add spool color
			spools[spool.type][spool.color_id] += spool.weight  # add spool weight
		return spools # {'PETG': {1: 998, 5: 4500, 7: 1000, 2: 1000}, 'PLA': {6: 9000}, 'PC': {1: 4000}, 'ABS': {6: 1000}, 'TPE': {9: 900}}

	def spools_average_price(self, materials): # materials: 'basic' or 'PETG' or ['PETG', 'PLA', 'basic',...]
		materials = self.normalize_materials(materials)
		price = 1
		weight = 1
		for spool in self.spools:
			if spool.type in materials:
				price += spool.price
				weight += spool.weight
		return int(price/weight)

	def get_gram_price(self, color_id, types):
		plastic_types = self.normalize_materials(types)
		if color_id != 0:
			for spool in self.spools:
				if spool.color_id == color_id and spool.type in plastic_types:
					gram_price = spool.price/spool.weight
					break
		else:
			gram_price = self.spools_average_price(plastic_types)
		return gram_price

	def available_weight(self, spool, minimal_weight):
		weight = spool.weight - spool.used - spool.booked - minimal_weight - 15
		if weight < 0 :
			return 0
		return weight

	def filament_available(self, statuses, type_, color_id, all_weight, one_copy_weight):
		spools = sorted(self.spools.copy(), key=lambda item: item.date)
		selected_spools = []
		small_spools = {}
		weight = 0
		for spool in spools:
			if all_weight > 0 and spool.status in statuses and spool.type == type_ and spool.color_id == color_id:
				spool_weight = self.available_weight(spool, 0)
				# 1) try to fit all order
				if spool_weight > all_weight:
					all_weight = 0
					selected_spools.append([spool, all_weight])
				# 2) try to fit several copies
				elif spool_weight > one_copy_weight:
					fits_weight = (spool_weight // one_copy_weight) * one_copy_weight
					all_weight -= fits_weight
					selected_spools.append([spool, fits_weight])
				# 3) spread copy over several spools
				elif spool_weight > 30:
					small_spools.append([spool, spool_weight])
					weight += spool_weight
					if weight > one_copy_weight:
						selected_spools.extend(small_spools)
						small_spools = []
						weight -= one_copy_weight
						all_weight -= one_copy_weight
		return selected_spools, all_weight

	def satisfy(self, statuses, types, color_id, order_weight, one_copy_weight):
		plastic_types = self.normalize_materials(types)
		booked = [] 
		for type_ in plastic_types:
			spools, order_weight = self.filament_available(statuses, type_, color_id, order_weight, one_copy_weight)
			booked.extend(spools)
			if order_weight < 1:
				return booked
		if order_weight > 0: return [] # Not enough spools to satisfy order
			
	def book(self, statuses, types, color_id, one_copy_weight, order_quantity):
		order_weight = one_copy_weight * order_quantity

		booked = self.satisfy(statuses, types, color_id, order_weight, one_copy_weight)
		if not booked: return
		books = []
		for spool_ in booked:
			spool = spool_[0]
			spool.booked += spool_[1]
			books.append([spool.id, spool_[1]])
			self.app.db.update_spool(spool)

		return books

#---------------------------- CLIENT VIEW FILAMENTS ----------------------------

	def get_all_buttons(self, status):  # get all spools of status and convert them to unique buttons
		spools_ = {}
		
		for spool in self.app.equipment.spools:
			if spool.status != status:
				continue
			type_color = (spool.type, spool.color_id)
			if type_color not in spools_:
				spools_[type_color] = (0, spool.delivery_date_estimate)
			total_weight, earliest_date = spools_[type_color]
			total_weight += spool.weight

			if earliest_date is None or (spool.delivery_date_estimate is not None and spool.delivery_date_estimate < earliest_date):
				earliest_date = spool.delivery_date_estimate

			spools_[type_color] = (total_weight, earliest_date)
		
		buttons = [
			[
				f"{type_} {self.color_logic.get_color_name(color_id)}: {self.app.functions.get_weight_string(weight)}" +
				(f" ({self.app.functions.russian_date_2(date)})" if status == 'ordered' else ''), 
				color_id
			]
			for (type_, color_id), (weight, date) in spools_.items()
		]
		buttons.sort(key=self.get_list_element_0)
		return buttons

	def is_anything_ordered(self):
		for spool in self.spools:
			if spool.status == 'ordered':
				return True
		return False

#---------------------------- CLIENT COLOR SELECTION ----------------------------

	def get_in_stock_buttons(self, types, one_copy_weight, order_quantity):
		buttons = []
		order_weight = one_copy_weight * order_quantity
		for color in self.get_colors(types):
			spools_ = self.satisfy(['stock'], types, color.id, order_weight, one_copy_weight)
			spools_ = [sublist[0] for sublist in spools_]
			if spools_:
				buttons.append([color.get_name(), color.id])
		return buttons

	def is_ordered(self, types, one_copy_weight, order_quantity):
		buttons = self.get_ordered_buttons(types, one_copy_weight, order_quantity)
		if buttons:
			return True
		return False

	def get_ordered_buttons(self, types, one_copy_weight, order_quantity):
		plastic_types = self.normalize_materials(types)
		order_weight = one_copy_weight * order_quantity

		ordered = []
		stock = []
		colors = set()
		latest_dates = {}

		# get a list of ordered colors
		for color in self.get_colors(types):
			ordered_spools = self.satisfy(['stock', 'ordered'], types, color.id, order_weight, one_copy_weight)
			stock_spools = self.satisfy(['stock'], types, color.id, order_weight, one_copy_weight)
			ordered_spools = [sublist[0] for sublist in ordered_spools]
			stock_spools = [sublist[0] for sublist in stock_spools]
			ordered.extend(ordered_spools)
			stock.extend(stock_spools)
			
		ordered = [spool for spool in ordered if spool not in stock] # remove color if stock buttons already contain it

		# get latest delivery date for each color
		for spool in ordered:
			if spool.color_id not in colors:
				colors.add(spool.color_id)
		for color in colors:
			latest_date = max(spool.delivery_date_estimate for spool in ordered if spool.color_id == color)
			latest_dates[color] = latest_date

		# convert to button format list
		return [[self.color_logic.get_color_name(key) + ' (' + self.app.functions.russian_date_2(value) + ')', key]
				for key, value in latest_dates.items()]

#---------------------------- LOGIC ----------------------------

	def normalize_materials(self, val):
		if type(val) == str:
			val = [val]
		if 'basic' in val:
			val.remove('basic')
			val.extend(self.app.setting.get('basic_plastic_types').split(','))
		return list(set(val)) # remove duplicates

	def get_colors(self, types):
		plastic_types = self.normalize_materials(types)
		colors = []
		for spool in self.spools:
			if spool.type in plastic_types:
				colors.append(self.color_logic.get_color(spool.color_id))
		return list(set(colors)) # remove duplicates

	def get_spool(self, id):
		for spool in self.spools:
			if spool.id == int(id):
				return spool

	def get_list_element_0(self, lst):
		return lst[0]