from datetime import date

class Surface:
	db = None

	id = '1'
	date: date
	type = ''

	def __init__(self, db, id, created, type):
		self.db = db
		self.id = id
		self.date = created
		self.type = type