from datetime import date

class Printer:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.name = ''
		self.type_ = ''