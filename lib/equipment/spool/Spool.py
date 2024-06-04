from datetime import date

class Spool:
	app = None

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

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.date = date.today()

	def available_weight(self):
		return self.weight - self.used