from datetime import date

class Container:
	app = None
	
	id = 1
	created: date
	type = ''
	capacity = 0

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()