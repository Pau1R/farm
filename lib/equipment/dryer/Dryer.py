from datetime import date

class Dryer:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.name = ''
		self.capacity = 0
		self.minTemp = 0
		self.maxTemp = 0
		self.maxTime = 0