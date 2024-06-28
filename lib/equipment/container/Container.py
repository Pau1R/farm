from datetime import date

class Container:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.type = ''
		self.capacity = 0