from datetime import date

class Spool:
	app = None
	db = None

	id = 1
	date: date
	type = ''
	diameter = 0.0
	weight = 0
	density = 0.0 # gramms per cm cube
	color_id = 0
	dried = ''
	brand = ''
	booked = 0
	used = 0
	price = 0
	status = ''
	delivery_date_estimate: date

	def __init__(self, app, db, id, created, type, diameter, weight, density, color_id, dried, brand, used, price, status, delivery_date_estimate):
		self.app = app
		self.db = db
		self.id = id
		self.date = created
		self.type = type
		self.diameter = diameter
		self.weight = int(weight)
		self.density = density
		self.color_id = color_id
		self.dried = dried
		self.brand = brand
		self.used = int(used)
		self.price = price
		self.status = status
		self.delivery_date_estimate = delivery_date_estimate

	def available_weight(self):
		return self.weight - self.used