from lib.request.Request import Request

class Request_logic:
	app = None
	requests = []
	
	def __init__(self, app):
		self.app = app
		self.requests = app.requests
		self.app.db.get_requests()

	def add_request(self, user_id, text):
		id = self.app.functions.get_next_free_id(self.requests)
		request = Request(self.app, id)
		request.user_id = user_id
		request.text = text
		self.requests.append(request)
		self.app.db.add_request(request)
		self.requests.sort(key=self.get_object_date)
		return request

	def remove_request(self, request):
		self.requests.remove(request)
		self.app.db.remove_request(request)

	def get_object_date(self, element):
		return element.date
		