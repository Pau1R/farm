from datetime import date

class Container:
	app = None
	
	id = 1
	date: date
	type = ''
	capacity = 0

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.date = date.today()