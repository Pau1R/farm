from datetime import date

class Printer:
	db = None

	id = '1'
	date: date
	name = ''
	type_ = ''

	def __init__(self, db, id, created, name, type_):
		self.db = db
		self.id = id
		self.date = created
		self.name = name
		self.type_ = type_