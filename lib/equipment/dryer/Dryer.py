from datetime import date

class Dryer:
	app = None

	id = 1
	created: date
	name = ''
	capacity = 0
	minTemp = 0
	maxTemp = 0
	maxTime = 0

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()