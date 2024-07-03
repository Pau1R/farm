import time
from datetime import date

class Clicker:
	
	def __init__(self, app):
		self.app = app
		self.now = int(time.time())
		self.sec2 = 0
		self.sec15 = 0
		self.sec30 = 0
		self.min1 = 0
		self.min5 = 0
		self.hour1 = 0
		self.day1 = 0


	def click(self):
		now = int(time.time())
		self.now = now
		if now > self.sec2 + 2:
			self.sec2 = now
			if now > self.sec15 + 15:
				self.sec15 = now
				if now > self.sec30 + 30:
					self.sec30 = now
					if now > self.min1 + 60: # 1 minute
						self.min1 = now
						self.app.order_logic.remove_unpaid_reserves()
						if now > self.min5 + 300: # 5 minutes
							self.min5 = now
							if now > self.hour1 + 3600: # 1 hour
								self.hour1 = now
								if now > self.day1 + 86400: # 1 day
									self.day1 = now
									self.remove_inactive_chats()

	def remove_inactive_chats(self):
		for chat in self.app.chats:
			if not chat.is_employee:
				period = (date.today() - chat.last_access_date).days
				if period < 30:
					break
				elif period < 60:
					for order in self.app.orders:
						if order.user_id == chat.user_id:
							break
				self.app.chats.remove(chat)