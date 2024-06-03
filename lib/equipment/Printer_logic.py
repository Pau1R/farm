

class Printer_logic:
	app = None
	printers = None

	def __init__(self, app):
		self.app = app
		self.printers = app.equipment.printers

	def get_average_load(self, printer_type):
		all_time = self.app.order_logic.count_all_time(printer_type)
		printers = self.get_printers_by_type(printer_type)
		return all_time/len(printers)

	def get_printers_by_type(self, type):
		printers = []
		for printer in self.printers:
			if printer.type == type:
				printers.append(printer)
		return printers