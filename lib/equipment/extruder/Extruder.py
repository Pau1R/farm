from datetime import date

class Extruder:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.name = ''
		self.maxTemp = 0
		self.nozzleDiameter = 0