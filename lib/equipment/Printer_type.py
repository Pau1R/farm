class Printer_type:
	db = None

	id = '1'
	name = ''
	hour_cost = 0

	def __init__(self, db, id, name, hour_cost):
		self.db = db
		self.id = id
		self.name = name
		self.hour_cost = hour_cost