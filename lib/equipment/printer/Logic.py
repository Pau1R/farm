class Printer_logic:

	def __init__(self, app):
		self.app = app

	def get_average_load(self, printer_type):
		all_time = self.app.order_logic.count_all_time(printer_type)
		printers = self.get_printers_by_type(printer_type)
		return all_time/len(printers)

	def get_printers_by_type(self, type_):
		printers = []
		for printer in self.app.equipment.printers:
			if printer.type_ == type_ or type_ == '*':
				printers.append(printer)
		return printers