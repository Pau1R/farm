
class Printer_type_logic:

	def __init__(self, app):
		self.app = app

	def get_printer_type(self, id):
		for printer_type in self.app.equipment.printer_types:
			if printer_type.id == int(id):
				return printer_type
		return ''

	def get_all_types(self):
		buttons = []
		for type_ in self.app.equipment.printer_types:
			buttons.append([type_.name, type_.id])
		return buttons