from datetime import date

class Printer:
	db = None

	id = '1'
	date: date
	name = ''

	def __init__(self, db, id, created, name):
		self.db = db
		self.id = id
		self.date = created
		self.name = name