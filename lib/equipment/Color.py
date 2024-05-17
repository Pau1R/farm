from datetime import date

class Color:
	db = None

	id = '1'
	date: date
	name = ''
	samplePhoto = ''
	
	def __init__(self, db, id, created, name, samplePhoto):
		self.db = db
		self.id = id
		self.date = created
		self.name = name
		self.samplePhoto = samplePhoto
