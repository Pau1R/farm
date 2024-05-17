import sqlite3
from datetime import date
from datetime import datetime
import os
from lib.Chat import Chat
from lib.client.Order import Order

class Database:
	cursor = None

	appRoot = os.getcwd()
	# appRoot = '/farm'
	dbPath = appRoot + '/farm.db'

	def __init__(self, app):
		self.app = app

		self.connect()

	def connect(self):
		if not os.path.exists(self.appRoot):
			os.mkdir(self.appRoot)
		self.db = sqlite3.connect(self.dbPath, check_same_thread=False)
		self.cursor = self.db.cursor()

		chat = """
			user_id INTEGER PRIMARY KEY,
			created DATETIME,
			name TEXT,
			isEmployee LOGICAL,
			roles TEXT,
			payId TEXT,
			balance TEXT"""
		container = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			type TEXT,
			capacity INTEGER"""
		dryer = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			name TEXT,
			capacity INTEGER,
			minTemp INTEGER,
			maxTemp INTEGER,
			maxTime INTEGER"""
		extruder = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			name TEXT,
			maxTemp INTEGER,
			nozzleDiameter INTEGER"""
		location = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			name TEXT,
			type TEXT"""
		printer = """
			id INTEGER PRIMARY KEY, 
			created DATETIME, 
			name TEXT"""
		spool = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			type TEXT,
			diameter DECIMAL,
			weight TEXT,
			density DECIMAL,
			color TEXT,
			dried TEXT,
			brand TEXT,
			used TEXT"""
		color = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			name TEXT,
			samplePhoto TEXT"""
		surface = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			type TEXT"""
		order = """
			order_id INTEGER PRIMARY KEY,
			created DATETIME,
			name TEXT,
			status TEXT,
			quantity INTEGER,
			support_time DECIMAL,
			support_remover TEXT,
			user_id TEXT,
			model_file TEXT,
			priority INTEGER,
			plastic_type TEXT,
			plastic_color TEXT,
			layer_hight DECIMAL,
			price_estimate DECIMAL,
			sketches TEXT,
			assinged_designer_id TEXT,
			weight DECIMAL,
			time DECIMAL,
			start_time_estimate DATETIME,
			end_time_estimate DATETIME,
			price DECIMAL,
			prepayed DECIMAL,
			prepayment_percent DECIMAL,
			conditions TEXT,
			comment TEXT """

		create = 'CREATE TABLE IF NOT EXISTS '
		
		self.cursor.execute(create + 'chat (' + chat + ')')
		self.cursor.execute(create + 'container (' + container + ')')
		self.cursor.execute(create + 'dryer (' + dryer + ')')
		self.cursor.execute(create + 'extruder (' + extruder + ')')
		self.cursor.execute(create + 'location (' + location + ')')
		self.cursor.execute(create + 'printer (' + printer + ')')
		self.cursor.execute(create + 'spool (' + spool + ')')
		self.cursor.execute(create + 'color (' + color + ')')
		self.cursor.execute(create + 'surface (' + surface + ')')
		self.cursor.execute(create + 'order_ (' + order + ')')
		self.db.commit()

#---------------------------- CHAT ----------------------------

	def get_chats(self):
		self.cursor.execute('SELECT * FROM chat')
		for row in self.cursor.fetchall():
			chat = Chat(self.app, str(row[0]), bool(row[3]), row[1])
			chat.user.name = row[2]
			if row[3]: # employee
				chat.user.roles = row[4].split(',')
				while ('' in chat.user.roles):
   					chat.user.roles.remove("")
			else:
				chat.user.payId = row[5]
				chat.user.balance = row[6]
			self.app.chats.append(chat)

	def create_chat(self, chat):
		if chat.is_employee:
			self.cursor.execute('INSERT OR IGNORE INTO chat VALUES (?,?,?,?,?,Null,Null)', (chat.user_id, date.today(), chat.user.name, chat.is_employee, ','.join(chat.user.roles)))
		else:
			self.cursor.execute('INSERT OR IGNORE INTO chat VALUES (?,?,?,?,Null,?,?)', (chat.user_id, date.today(), chat.user.name, chat.is_employee, chat.user.payId, chat.user.balance))
		self.db.commit()

	def update_chat(self, chat):
		values = 'user_id = "' + chat.user_id + '", '
		values += 'created = "' + str(chat.created) + '", '
		values += 'name = "' + chat.user.name + '", '
		values += 'isEmployee = "' + str(chat.is_employee) + '", '
		if chat.is_employee:
			chat.user.roles.append('')
			while ("" in chat.user.roles):
   				chat.user.roles.remove("")
			values += 'roles = "' + ','.join(chat.user.roles) + '" '
		else:
			values += 'payId = "' + chat.user.payId + '", '
			values += 'balance = "' + chat.user.balance + '" '
		self.cursor.execute('UPDATE chat SET ' + values + ' WHERE user_id = ' + str(chat.user_id))
		self.db.commit()

	def remove_chat(self, chat):
		self.cursor.execute('DELETE FROM chat WHERE user_id=?', (chat.user_id,))
		self.db.commit()

#---------------------------- ORDER ----------------------------

	def get_orders(self):
		self.cursor.execute('SELECT * FROM order_')
		sql = self.cursor.fetchall()
		orders = []
		for line in sql:
			order = Order(self.app, line[0])
			order.created = line[1]
			order.name = line[2]
			order.status = line[3]
			order.quantity = line[4]
			order.support_time = line[5]
			order.support_remover = line[6]
			order.user_id = line[7]
			order.model_file = line[8]
			order.priority = line[9]
			order.plastic_type = line[10]
			order.plastic_color = line[11]
			order.layer_hight = line[12]
			order.price_estimate = line[13]
			order.sketches = line[14]
			order.assinged_designer_id = line[15]
			order.weight = line[16]
			order.time = line[17]
			try:
				order.start_time_estimate = datetime.strptime(line[18], '%m/%d/%y %H:%M:%S')
			except:
				order.start_time_estimate = None
			# order.end_time_estimate = line[19]
			order.price = line[20]
			order.prepayed = line[21]
			order.prepayment_percent = line[22]
			order.comment = line[23]
			order.conditions = line[24]
			self.app.orders.append(order)

	def create_order(self, order):
		self.cursor.execute('INSERT INTO order_ VALUES (?,?,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null,Null)', (order.order_id, date.today()))

		# self.cursor.execute('INSERT OR IGNORE INTO order_ VALUES (order_id, created)', (order.order_id, date.today()))
		self.db.commit()
		self.update_order(order)

	def update_order(self, order):
		values = 'name = "' + order.name + '", '
		values += 'status = "' + order.status + '", '
		values += 'quantity = "' + str(order.quantity) + '", '
		values += 'support_time = "' + str(order.support_time) + '", '
		values += 'support_remover = "' + str(order.support_remover) + '", '
		values += 'user_id = "' + order.user_id + '", '
		values += 'model_file = "' + order.model_file + '", '
		values += 'priority = "' + str(order.priority) + '", '
		values += 'plastic_type = "' + order.plastic_type + '", '
		values += 'plastic_color = "' + order.plastic_color + '", '
		values += 'layer_hight = "' + str(order.layer_hight) + '", '
		values += 'price_estimate = "' + str(order.price_estimate) + '", '
		values += 'sketches = "' + str(order.sketches) + '", '
		values += 'assinged_designer_id = "' + order.assinged_designer_id + '", '
		values += 'weight = "' + str(order.weight) + '", '
		values += 'time = "' + str(order.time) + '", '
		values += 'start_time_estimate = "' + str(order.start_time_estimate) + '", '
		values += 'end_time_estimate = "' + str(order.end_time_estimate) + '", '
		values += 'price = "' + str(order.price) + '", '
		values += 'prepayed = "' + str(order.prepayed) + '", '
		values += 'prepayment_percent = "' + str(order.prepayment_percent) + '", '
		values += 'conditions = "' + order.conditions + '", '
		values += 'comment = "' + order.comment + '" '
		self.cursor.execute('UPDATE order_ SET ' + values + ' WHERE order_id = ' + str(order.order_id))
		self.db.commit()

	def remove_order(self, order):
		self.cursor.execute('DELETE FROM order_ WHERE order_id=?', (order.order_id,))
		self.db.commit()

#---------------------------- EQUIPMENT ----------------------------

	def get_containers(self):
		self.cursor.execute('SELECT id, created, type, capacity FROM container')
		sql = self.cursor.fetchall()
		containers = []
		for container in sql:
			containers.append([str(container[0]), container[1], container[2], container[3]])
		return containers

	def add_container(self, container):
		self.cursor.execute('INSERT INTO container VALUES (?,?,?,?)', (container.id, date.today(), container.type, container.capacity))
		self.db.commit()

	def remove_container(self, id):
		self.cursor.execute('DELETE FROM container WHERE id=?', (id,))
		self.db.commit()


	def get_dryers(self):
		self.cursor.execute('SELECT id, created, name, capacity, minTemp, maxTemp, maxTime FROM dryer')
		sql = self.cursor.fetchall()
		dryers = []
		for dryer in sql:
			dryers.append([str(dryer[0]), dryer[1], dryer[2], dryer[3], dryer[4], dryer[5], dryer[6]])
		return dryers

	def add_dryer(self, dryer):
		self.cursor.execute('INSERT INTO dryer VALUES (?,?,?,?,?,?,?)', (dryer.id, date.today(), dryer.name, dryer.capacity, dryer.minTemp, dryer.maxTemp, dryer.maxTime))
		self.db.commit()

	def remove_dryer(self, id):
		self.cursor.execute('DELETE FROM dryer WHERE id=?', (id,))
		self.db.commit()

	def get_extruders(self):
		self.cursor.execute('SELECT id, created, name, maxTemp, nozzleDiameter FROM extruder')
		sql = self.cursor.fetchall()
		extruders = []
		for extruder in sql:
			extruders.append([str(extruder[0]), extruder[1], extruder[2], extruder[3], extruder[4]])
		return extruders

	def add_extruder(self, extruder):
		self.cursor.execute('INSERT INTO extruder VALUES (?,?,?,?,?)', (extruder.id, date.today(), extruder.name, extruder.maxTemp, extruder.nozzleDiameter))
		self.db.commit()

	def remove_extruder(self, id):
		self.cursor.execute('DELETE FROM extruder WHERE id=?', (id,))
		self.db.commit()

	def get_locations(self):
		self.cursor.execute('SELECT id, created, name, type FROM location')
		sql = self.cursor.fetchall()
		locations = []
		for location in sql:
			locations.append([str(location[0]), location[1], location[2], location[3]])
		return locations

	def add_location(self, location):
		self.cursor.execute('INSERT INTO location VALUES (?,?,?,?)', (location.id, date.today(), location.name, location.type))
		self.db.commit()

	def remove_location(self, id):
		self.cursor.execute('DELETE FROM location WHERE id=?', (id,))
		self.db.commit()

	def get_printers(self):
		self.cursor.execute('SELECT id, created, name FROM printer')
		sql = self.cursor.fetchall()
		printers = []
		for printer in sql:
			printers.append([str(printer[0]), printer[1], printer[2]])
		return printers

	def add_printer(self, printer):
		self.cursor.execute('INSERT INTO printer VALUES (?,?,?)', (printer.id, date.today(), printer.name))
		self.db.commit()

	def remove_printer(self, id):
		self.cursor.execute('DELETE FROM printer WHERE id=?', (id,))
		self.db.commit()

	def get_spools(self):
		self.cursor.execute('SELECT id, created, type, diameter, weight, density, color, dried, brand, used FROM spool')
		sql = self.cursor.fetchall()
		spools = []
		for spool in sql:
			spools.append([str(spool[0]), spool[1], spool[2], float(spool[3]), int(spool[4]), float(spool[5]), spool[6], spool[7], spool[8], int(spool[9])])
		return spools

	def add_spool(self, spool):
		self.cursor.execute('INSERT INTO spool VALUES (?,Null,Null,Null,Null,Null,Null,Null,Null,Null)', (spool.id,))
		self.db.commit()
		self.update_spool(spool)

	def update_spool(self, spool):
		values = 'created = "' + str(spool.date) + '", '
		values += 'type = "' + spool.type + '", '
		values += 'diameter = "' + str(spool.diameter) + '", '
		values += 'weight = "' + str(spool.weight) + '", '
		values += 'density = "' + str(spool.density) + '", '
		values += 'color = "' + spool.color + '", '
		values += 'dried = "' + str(spool.dried) + '", '
		values += 'brand = "' + spool.brand + '", '
		values += 'used = "' + str(spool.used) + '" '
		self.cursor.execute('UPDATE spool SET ' + values + ' WHERE id = ' + str(spool.id))
		self.db.commit()

	def remove_spool(self, id):
		self.cursor.execute('DELETE FROM spool WHERE id=?', (id,))
		self.db.commit()

	def get_colors(self):
		self.cursor.execute('SELECT id, created, name, samplePhoto FROM color')
		sql = self.cursor.fetchall()
		colors = []
		for color in sql:
			colors.append([str(color[0]), color[1], color[2], color[3]])
		return colors

	def add_color(self, color):
		self.cursor.execute('INSERT INTO color VALUES (?,Null,Null,Null)', (color.id,))
		self.db.commit()
		self.update_color(color)

	def update_color(self, color):
		values = 'created = "' + str(color.date) + '", '
		values += 'name = "' + color.name + '", '
		values += 'samplePhoto = "' + color.samplePhoto + '" '
		self.cursor.execute('UPDATE color SET ' + values + ' WHERE id = ' + str(color.id))
		self.db.commit()

	def remove_color(self, id):
		self.cursor.execute('DELETE FROM color WHERE id=?', (id,))
		self.db.commit()
	
	def get_surfaces(self):
		self.cursor.execute('SELECT id, created, type FROM surface')
		sql = self.cursor.fetchall()
		surfaces = []
		for surface in sql:
			surfaces.append([str(surface[0]), surface[1], surface[2]])
		return surfaces

	def add_surface(self, surface):
		self.cursor.execute('INSERT INTO surface VALUES (?,?,?)', (surface.id, date.today(), surface.type))
		self.db.commit()

	def remove_surface(self, id):
		self.cursor.execute('DELETE FROM surface WHERE id=?', (id,))
		self.db.commit()
