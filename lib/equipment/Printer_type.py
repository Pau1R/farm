class Printer_type:
	app = None

	id = 1
	name = ''
	hour_cost = 0

	def __init__(self, app, id):
		self.app = app
		self.id = id