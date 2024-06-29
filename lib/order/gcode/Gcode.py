
class Gcode:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.order_id = 0
		self.file_id = ''
		self.screenshot = ''
		self.status = ''
		self.duration = 0
		self.start_datetime = None
		
		self.quantity = 1 # temporary value for created gcodes