from datetime import date

class Container:
	db = None

	id = '1'
	date: date
	type = 'box'
	capacity = 0

	def __init__(self, db, id, created, type, capacity):
		self.db = db
		self.id = id
		self.date = date.today()
		self.type = type
		self.capacity = capacity