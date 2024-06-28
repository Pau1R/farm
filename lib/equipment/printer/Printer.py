from datetime import date

class Printer:
	app = None

	id = 1
	created: date
	name = ''
	type_ = ''

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()