from datetime import date

class Location:
	db = None

	id = '1'
	date: date
	name = ''
	type = ''

	def __init__(self, db, id, created, name, type):
		self.db = db
		self.id = id
		self.date = created
		self.name = name
		self.type = type