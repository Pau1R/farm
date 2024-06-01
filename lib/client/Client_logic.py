from lib.client.Texts import Texts
import json

class Client_logic:
	equipment = None
	orders = None
	texts = None

	def __init__(self, app, orders):
		self.equipment = app.equipment
		self.orders = orders
		self.texts = Texts(app)
