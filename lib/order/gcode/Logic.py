
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

	def get_gcodes(self, order):
		gcodes = []
		for gcode in self.gcodes:
			if gcode.order_id == order.id:
				gcodes.append(gcode)
		return gcodes

	def remove_reserve(self, order):
		gcodes = self.get_gcodes(order)
		for gcode in gcodes:
			for spool in gcode.booked:
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
		gcodes = sorted(gcodes, key=lambda gcode: gcode.weight, reverse=True) # satisfy big gcodes first
		gcode_spools = {}
		for gcode in gcodes:
			# get spool assignment variants
			satisfy = self.app.equipment.spool_logic.satisfy
			variants = []
			variants.append(satisfy(statuses, order.plastic_type, color_id, gcode.weight, gcode.weight))
			if len(variants[0]) != 1:
				variants.append(satisfy(statuses, order.plastic_type, color_id, gcode.weight, int(gcode.weight/2)))
				if len(variants[1]) != 1:
					variants.append(satisfy(statuses, order.plastic_type, color_id, gcode.weight, int(gcode.weight/4)))
					if len(variants[2]) != 1:
						variants.append(satisfy(statuses, order.plastic_type, color_id, gcode.weight, int(gcode.weight/8)))
			# get the minimum spools amount variant
			shortest = float('inf')
			smallest_variant = []
			for l in variants:
				if len(l) > 0 and len(l) < shortest:
					shortest = len(l)
					smallest_variant = l
			if not smallest_variant:
				return []
			# save info to all
			gcode_spools[gcode] = []
			for spool in smallest_variant:
				gcode_spools[gcode].append([spool[0].id, spool[1]])
		return gcode_spools

	def book(self, order, statuses, color_id):
		gcode_spools = self.smallest_variants(order, statuses, color_id)
		for gcode, spools in gcode_spools.items():
			gcode.booked = spools
			self.app.db.update_gcode(gcode)
			for spool in spools:
				weight = spool[1]
				spool = self.app.equipment.spool_logic.get_spool(spool[0])
				spool.booked += weight
				self.app.db.update_spool(spool)