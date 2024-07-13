from datetime import date

class Surface:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.location_type = 0
		self.location = 0
		self.type = ''