from datetime import date

class Location:
	app = None

	id = 1
	date: date
	name = ''
	type = ''

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.date = date.today()