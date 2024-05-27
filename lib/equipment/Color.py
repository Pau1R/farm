from datetime import date

class Color:
	db = None

	id = 0
	date: date
	name = ''
	parent_id = 0
	samplePhoto = ''
	
	def __init__(self, app, db, id, created, name, parent_id, samplePhoto):
		self.app = app
		self.db = db
		self.id = id
		self.date = created
		self.name = name
		self.parent_id = parent_id
		self.samplePhoto = samplePhoto

	def get_color_name(self):
		if self.parent_id == 0:
			return self.name
		else:
			for color in self.app.equipment.colors:
				if color.id == self.parent_id:
					return color.name + '-' + self.name.lower()