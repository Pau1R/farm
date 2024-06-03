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

	def get_order_by_id(self, order_id):
		for order in self.orders:
			if order.id == order_id:
				return order

	def get_client_orders(self, user_id):
		orders = []
		for order in self.orders:
			if order.user_id == user_id:
				orders.append(order)
		return orders

	def get_order_by_pay_code(self, pay_code):
		for order in self.orders:
			if order.pay_code == pay_code:
				return order

	def get_order_by_delivery_code(self, delivery_code):
		for order in self.orders:
			if order.delivery_code == delivery_code:
				return order