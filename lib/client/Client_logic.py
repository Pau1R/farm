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

	def available_materials(self):
		spools = self.equipment.spool_logic.available_spools()
		for order in self.orders:
			if not (order.plastic_type == '' or order.plastic_type == None):
				mini = spools[order.plastic_type]
				weight = 0
				if order.color_id in mini:
					weight = mini[order.color_id]
				mini[order.color_id] = weight - order.weight
				if order.weight >= weight:afazS
				if spools[order.plastic_type] == {}:
					del spools[order.plastic_type]

		text = ''
		for type in spools:
			text += '\n' + type + ':'
			mini = spools[type]
			for color in mini:
				text += '\n▪️ ' + color + ' ' + str(mini[color]/1000) + ' кг'
		return self.texts.available_materials + '\n' + text
	