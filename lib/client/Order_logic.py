import time

class Order_logic:
	app = None

	def __init__(self, app):
		self.app = app
		self.orders = app.orders

	def remove_unpaid_reserves(self):
		now = int(time.time())
		for order in self.orders:
			if not order.is_prepayed():
				if now > order.booked_time + 1200:
					order.remove_reserve()