from datetime import date

class Printer:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.location_type = 0
		self.location = 0
		self.name = ''
		self.type_ = 0

	def type(self):
		for type_ in self.app.equipment.printer_types:
			if type_.id == self.type_:
				return type_