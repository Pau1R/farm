from datetime import date

class Request:
	app = None

	id = 0
	client_id = 0
	date = None
	text = ''
	
	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.date = date.today()