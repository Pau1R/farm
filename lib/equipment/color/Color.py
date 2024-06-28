from datetime import date

class Color:
	
	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.name = ''
		self.parent_id = 0
		self.samplePhoto = ''

	def get_name(self):
		if self.parent_id == 0:
			return self.name
		else:
			for color in self.app.equipment.colors:
				if color.id == self.parent_id:
					return color.name + '-' + self.name.lower()