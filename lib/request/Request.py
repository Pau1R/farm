from datetime import date

class Request:
	app = None

	id = 0
	client_id = 0
	created = None
	text = ''
	
	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()