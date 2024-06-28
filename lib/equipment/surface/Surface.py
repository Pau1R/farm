from datetime import date

class Surface:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.type = ''