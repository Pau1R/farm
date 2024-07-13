class Color_logic:
	
	def __init__(self, app):
		self.app = app
		self.colors = app.equipment.colors

	def get_color_name(self, id):
		colors = self.app.equipment.colors
		for color in colors:
			if color.id == int(id):
				return color.get_name()
		return ''

	def get_color(self, id):
		for color in self.colors:
			if color.id == int(id):
				return color

	def get_color_photo(self, id):
		for color in self.colors:
			if color.id == int(id):
				return color.samplePhoto