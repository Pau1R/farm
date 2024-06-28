from datetime import date

class Color:
	app = None

	id = 0
	created: date
	name = ''
	parent_id = 0
	samplePhoto = ''
	
	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()

	def get_name(self):
		if self.parent_id == 0:
			return self.name
		else:
			for color in self.app.equipment.colors:
				if color.id == self.parent_id:
					return color.name + '-' + self.name.lower()