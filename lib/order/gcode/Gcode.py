
class Gcode:
	app = None

	id = 0
	order_id = 0
	file_id = ''
	screenshot = ''
	status = ''
	duration = 0

	quantity = 1 # temporary value for created gcodes

	def __init__(self, app, id):
		self.app = app
		self.id = id
