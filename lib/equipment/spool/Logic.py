from datetime import date

class Spool_logic:

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

	def available_weight(self, spool):
		weight = spool.weight - spool.used - spool.booked - 15
		if weight < 0 :
			weight = 0
		return int(weight)

	def filament_available(self, statuses, type_, color_id, all_weight, one_copy_weight):
		# There is a list of spools. Each spool contains type, weight (usually 1 kg), booked_weight, used_weight, color and status. Some spools are partially booked or used.
		# Now a new order comes in and spools need to be booked. The order type is PETG, amount of copies is 6, one copy weight is 200 grams, color is black and status is stock.
		# Write an algorithm that looks over the spools and optimizes their usage so the spools with the smallest amount of remaining weight are used first. Remaining weight should be enough for at least one copy
		if color_id == 2 and len(statuses) > 1:
			x = ''
		spools = [spool for spool in self.spools.copy() if spool.type == type_ and spool.color_id == color_id and spool.status in statuses]
		if not spools:
			return []
		spools = sorted(spools, key=lambda spool: (self.available_weight(spool), spool.created))
		selected_spools = []
		small_spools = []
		small_weight = 0

		for spool in spools:
			spool_weight = self.available_weight(spool)
			if all_weight < 1:
				break
			# 1) try to fit all order
			elif spool_weight > all_weight:
				selected_spools.append([spool, all_weight])
				all_weight = 0
			# 2) try to fit several copies
			elif spool_weight > one_copy_weight:
				fits_weight = int((spool_weight // one_copy_weight) * one_copy_weight)
				all_weight -= fits_weight
				selected_spools.append([spool, fits_weight])
				# save remainder for (3)
				if spool_weight - fits_weight > 30:
					small_spools.append([spool, spool_weight - fits_weight])
					small_weight += spool_weight
			# 3) gather info for spreading copy over several spools
			elif spool_weight > 30:
				small_spools.append([spool, self.available_weight(spool)])
				small_weight += spool_weight

		if all_weight > 0:
			small_spools = sorted(small_spools, key=lambda spool: self.available_weight(spool[0]), reverse=True) # sort from heaviest to lightest
			for spool in small_spools:
				spool_weight = spool[1]
				spool = spool[0]
				if all_weight < spool_weight:
					spool_weight = all_weight
				all_weight -= spool_weight
				selected_spools.append([spool, spool_weight])
		if all_weight > 0:
			return []
		return selected_spools

	def satisfy(self, statuses, types, color_id, order_weight, one_copy_weight):
		plastic_types = self.normalize_materials(types)
		booked = []
		for type_ in plastic_types:
			spools = self.filament_available(statuses, type_, color_id, order_weight, one_copy_weight)
			booked.extend(spools)
		return booked
			
	def book(self, statuses, types, color_id, one_copy_weight, order_quantity):
		order_weight = int(one_copy_weight * order_quantity)

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
			latest_date = max(spool.delivery_date_estimate for spool in ordered if spool.color_id == color and spool.delivery_date_estimate is not None)
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

	def get_all_types(self):
		types = []
		for spool in self.spools:
			if spool.type not in types:
				types.append(spool.type)
		return types

	def get_list_element_0(self, lst):
		return lst[0]