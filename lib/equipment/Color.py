from datetime import date

class Color:
	db = None

	id = 0
	date: date
	name = ''
	parent_id = 0
	samplePhoto = ''
	
	def __init__(self, db, id, created, name, parent_id, samplePhoto):
		self.db = db
		self.id = id
		self.date = created
		self.name = name
		self.parent_id = parent_id
		self.samplePhoto = samplePhoto
