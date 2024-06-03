from datetime import date

class Printer:
	app = None

	id = 1
	date: date
	name = ''
	type_ = ''

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.date = date.today()