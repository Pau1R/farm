from datetime import date

class Request:

	def __init__(self, app, id):
		self.app = app
		self.id = id
		self.created = date.today()
		self.client_id = 0
		self.text = ''