from datetime import date

class Extruder:
	app = None

	id = 1
	date: date
	name = ''
	maxTemp = 0
	nozzleDiameter = 0

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.date = date.today()