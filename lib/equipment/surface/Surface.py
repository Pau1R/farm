from datetime import date

class Surface:
	app = None

	id = 1
	created: date
	type = ''

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()