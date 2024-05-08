from datetime import date

class Dryer:
	db = None

	id = '1'
	date: date
	name = ''
	capacity = 0
	minTemp = 0
	maxTemp = 0
	maxTime = 0

	def __init__(self, db, id, created, name, capacity, minTemp, maxTemp, maxTime):
		self.db = db
		self.id = id
		self.date = created
		self.name = name
		self.capacity = capacity
		self.minTemp = minTemp
		self.maxTemp = maxTemp
		self.maxTime = maxTime