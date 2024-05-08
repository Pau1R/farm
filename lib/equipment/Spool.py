from datetime import date

class Spool:
	db = None

	id = '1'
	date: date
	type = ''
	diameter = 0.0
	weight = 0
	density = 0.0 # gramms per cm cube
	color = ''
	dried = ''
	brand = ''
	booked = 0
	used = 0
	price = 0

	def __init__(self, db, id, created, type, diameter, weight, density, color, dried, brand, used):
		self.db = db
		self.id = id
		self.date = created
		self.type = type
		self.diameter = diameter
		self.weight = int(weight)
		self.density = density
		self.color = color
		self.dried = dried
		self.brand = brand
		self.used = int(used)

	def available_weight(self):
		return self.weight - self.used
