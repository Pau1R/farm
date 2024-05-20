from datetime import date

class Color:
	db = None

	id = '1'
	date: date
	name = ''
	shade = ''
	samplePhoto = ''
	
	def __init__(self, db, id, created, name, shade, samplePhoto):
		self.db = db
		self.id = id
		self.date = created
		self.name = name
		self.shade = shade
		self.samplePhoto = samplePhoto
