from datetime import date

class Spool:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.type = ''
		self.diameter = 0.0
		self.weight = 0
		self.density = 0.0 # gramms per cm cube
		self.color_id = 0
		self.dried = ''
		self.brand = ''
		self.booked = 0
		self.used = 0
		self.price = 0
		self.status = ''
		self.delivery_date_estimate: date

	def available_weight(self):
		return self.weight - self.used