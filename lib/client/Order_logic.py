import time

class Order_logic:
	app = None

	def __init__(self, app):
		self.app = app
		self.orders = app.orders

	def remove_unpaid_reserves(self):
		now = int(time.time())
		for order in self.orders:
			if not order.is_prepayed() and order.booked:
				if now > order.booked_time + 1800: # 30 minutes to prepay
					order.remove_reserve()
					chat = self.app.get_chat(order.user_id)
					chat.user.client_order.show_booking_canceled(self)