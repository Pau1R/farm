class Color_logic:
	app = None
	colors = []

	def __init__(self, app):
		self.app = app
		self.colors = app.equipment.colors

	def get_color_name(self, id):
		colors = self.app.equipment.colors
		for color in colors:
			if color.id == int(id):
				if color.parent_id == 0:
					return color.name
				else:
					for col in colors:
						if col.id == color.parent_id:
							return col.name + '-' + color.name.lower()

	def get_color(self, id):
		for color in self.colors:
			if color.id == int(id):
				return color

	def get_color_photo(self, id):
		for color in self.colors:
			if color.id == int(id):
				return color.samplePhoto