
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