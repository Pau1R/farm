from datetime import date

class Extruder:
	db = None

	id = '1'
	date: date
	name = ''
	maxTemp = 0
	nozzleDiameter = 0

	def __init__(self, db, id, created, name, maxTemp, nozzle):
		self.db = db
		self.id = id
		self.date = created
		self.name = name
		self.maxTemp = maxTemp
		self.nozzleDiameter = nozzle