
class Gcode_logic:

	def __init__(self, app):
		self.app = app
		self.orders = app.orders
		self.gcodes = app.gcodes

	def get_all_time(self, order):
		time = 0
		for gcode in self.gcodes:
			if gcode.order_id == order.id:
				time += gcode.duration
		return time

	def get_gcode(self, id):
		for gcode in self.gcodes:
			if gcode.id == int(id):
				return gcode

	def get_gcodes(self, order):
		gcodes = []
		for gcode in self.gcodes:
			if gcode.order_id == order.id:
				gcodes.append(gcode)
		return gcodes

	def remove_reserve(self, order):
		gcodes = self.get_gcodes(order)
		for gcode in gcodes:
			booked = gcode.booked
			if booked:
				for spool in booked:
					weight = spool[1]
					spool = self.app.equipment.spool_logic.get_spool(spool[0])
					if spool.booked >= weight:
						spool.booked -= weight
						self.app.db.update_spool(spool)
				gcode.booked = []
				self.app.db.update_gcode(gcode)

	def is_booked(self, order):
		gcodes = self.get_gcodes(order)
		for gcode in gcodes:
			if gcode.booked:
				return True
		return False

	def smallest_variants(self, order, statuses, color_id):
		gcodes = self.get_gcodes(order)
		gcodes = sorted(gcodes, key=lambda gcode: gcode.weight, reverse=True)  # satisfy big gcodes first
		gcode_spools = {}
		temp_book = []
		
		for gcode in gcodes:
			satisfy = self.app.equipment.spool_logic.satisfy
			variants = []
			weight_fractions = [1, 2, 4, 8]

			for fraction in weight_fractions:
				variant = satisfy(statuses, order.plastic_type, color_id, gcode.weight, int(gcode.weight / fraction))
				if variant:
					variants.append(variant)
				else:
					print('error: plastic not found')
				if len(variant) == 1:
					break

			shortest = float('inf')
			smallest_variant = []
			for variant in variants:
				if 0 < len(variant) < shortest:
					shortest = len(variant)
					smallest_variant = variant

			if not smallest_variant:
				return []

			# temp book
			temp_book.extend(smallest_variant)
			for spool in smallest_variant:
				spool[0].booked += spool[1]

			gcode_spools[gcode] = [[spool[0].id, spool[1]] for spool in smallest_variant]

		# remove temp booking
		for spool in temp_book:
			spool[0].booked -= spool[1]

		return gcode_spools

	def book(self, order, statuses, color_id):
		gcode_spools = self.smallest_variants(order, statuses, color_id)
		if not gcode_spools:
			return {}
		for gcode, spools in gcode_spools.items():
			gcode.booked = spools
			self.app.db.update_gcode(gcode)
			for spool_id, weight in spools:
				spool = self.app.equipment.spool_logic.get_spool(spool_id)
				spool.booked += weight
				self.app.db.update_spool(spool)
		return gcode_spools