
class Spool_logic:
	app = None
	spools = []

	def init(self, app, spools):
		self.app = app
		self.spools = spools

	def available_spools(self): # get all spools, return format: {type: {color_id: total_weight, ...}, ...}
	    spools = {}
	    for spool in self.spools:
	        if spool.type not in spools:
	            spools[spool.type] = {}  # add spool type
	        if spool.color_id not in spools[spool.type]:
	            spools[spool.type][spool.color_id] = 0  # add spool color
	        spools[spool.type][spool.color_id] += spool.weight  # add spool weight
	    return spools # {'PETG': {1: 998, 5: 4500, 7: 1000, 2: 1000}, 'PLA': {6: 9000}, 'PC': {1: 4000}, 'ABS': {6: 1000}, 'TPE': {9: 900}}

	def spools_average_price(self, materials): # materials: 'any' or 'PETG' or ['PETG', 'PLA', 'any',...]
		materials = normalize_materials(materials)
		price = 1
		weight = 1
		for spool in self.spools:
			if spool.type in materials:
				price += spool.price
				weight += spool.weight
		return int(price/weight)

	def get_gram_price(color_id, plastic_type):
		if color_id != 0:
			for spool in self.spools:
				if spool.color_id == color_id and spool.type == plastic_type:
					gram_price = spool.price/spool.weight
					break
		else:
			gram_price = self.spools_average_price(plastic_type)
		return gram_price

	def normalize_materials(val):
		if type(val) == str:
			val = [val]
		elif 'any' in val:
			val.remove('any')
			val.extend(self.app.settings.get('basic_plastic_types').split(','))
		val = list(set(val)) # remove duplicates
		return val

	def available_weight(self, spool, minimal_weight):
		weight = spool.weight - spool.used - spool.booked - minimal_weight - 15
		if weight < 0 :
			return 0
		return weight

	def filament_available(self, type_, color_id, all_weight, one_copy_weight):
		spools = sorted(self.spools.copy(), key=lambda item: item.date)
		selected_spools = []
		small_spools = {}
		weight = 0
		for spool in spools:
			if all_weight > 0 and spool.type == type_ and spool.color_id == color_id:
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
				# 3) spread copy over several spools of the same type
				elif spool_weight > 30:
					small_spools.append([spool, spool_weight])
					weight += spool_weight
					if weight > one_copy_weight:
						selected_spools.extend(small_spools)
						small_spools = []
						weight -= one_copy_weight
						all_weight -= one_copy_weight
		return selected_spools, all_weight

	def book(self, types, color_id, one_copy_weight, order_quantity):
		booked = [] 
		plastic_types = self.normalize_materials(types)
		order_weight = one_copy_weight * order_quantity

		for type_ in plastic_types:
			spools, order_weight = self.filament_available(type_, color_id, order_weight, one_copy_weight)
			booked.extend(spools)
			if order_weight < 1:
				break
		if order_weight > 0: # Not enough spools to satisfy order
			return None
		
		books = []
		for spool_ in booked:
			spool = spool_[0]
			spool.booked += spool_[1]
			books.append([spool.id, spool_[1]])
			self.app.db.update_spool(spool)

		return books

	def get_all_buttons(self, status) # get all spools of status and convert them to unique buttons
		spools_ = {}
		for spool in self.app.equipment.spools:
			if spool.status != status:
				continue
			type_color = (spool.type, spool.color_id)
			if type_color not in spools_:
				spools_[type_color] = (0, spool.delivery_date_estimate)
			total_weight, earliest_date = spools_[type_color]
			total_weight += spool.weight
			earliest_date = min(earliest_date, spool.delivery_date_estimate)
			spools_[type_color] = (total_weight, earliest_date)

		buttons = [
	        [f"{type_} {color_id}: {self.app.functions.get_weight_string(weight)}" + (f" ({self.app.functions.russian_date(date)})" if status == 'ordered' else ''), color_id]
	        for (type_, color_id), (weight, date) in spools_.items()
	    ]
		return buttons



	def is_anything_ordered(self):
		for spool in self.spools:
			if spool.status == 'ordered':
				return True
		return False


	def get_in_stock_buttons(self, type_):

	def is_ordered(self, type_):

	def get_ordered_buttons(self, type_):
		# Create a set of (color_id, type) for spools with status 'stock'
		stock_spools = {(spool.color_id, spool.type) for spool in spools if spool.status == 'stock'}

		# Create a dictionary to ensure uniqueness by (color_id, type)
		unique_ordered_spools = {}

		for spool in spools:
		    if spool.status == 'ordered' and (spool.color_id, spool.type) not in stock_spools:
		        key = (spool.color_id, spool.type)
		        if key not in unique_ordered_spools:
		            unique_ordered_spools[key] = spool

		# Convert the dictionary values to a list
		ordered_spools = list(unique_ordered_spools.values())

		# Print the result
		for spool in ordered_spools:
		    print(f"ID: {spool.id}, Color ID: {spool.color_id}, Type: {spool.type}, Status: {spool.status}")
