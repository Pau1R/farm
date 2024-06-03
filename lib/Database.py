import sqlite3
from datetime import date
from datetime import datetime
import os
from lib.Chat import Chat
from lib.client.Order import Order
from lib.equipment.Container import Container
from lib.equipment.Dryer import Dryer
from lib.equipment.Spool import Spool
from lib.equipment.Extruder import Extruder
from lib.equipment.Location import Location
from lib.equipment.Printer_type import Printer_type
from lib.equipment.Printer import Printer
from lib.equipment.Spool import Spool
from lib.equipment.Spool_logic import Spool_logic
from lib.equipment.Color import Color
from lib.equipment.Color_logic import Color_logic
from lib.equipment.Surface import Surface
import time
import ast

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
			money_payed DECIMAL,
			last_access_date DATETIME,
			orders_canceled INTEGER,
			limit_date DATETIME
			"""
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
		printer_type = """
			id INTEGER PRIMARY KEY,  
			name TEXT,
			hour_cost INTEGER"""
		printer = """
			id INTEGER PRIMARY KEY, 
			created DATETIME, 
			name TEXT,
			type TEXT"""
		spool = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			type TEXT,
			diameter DECIMAL,
			weight TEXT,
			density DECIMAL,
			color_id TEXT,
			dried TEXT,
			brand TEXT,
			booked INTEGER,
			used TEXT,
			price INTEGER,
			status TEXT,
			delivery_date_estimate DATETIME"""
		color = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			name TEXT,
			parent_id INTEGER,
			samplePhoto TEXT"""
		surface = """
			id INTEGER PRIMARY KEY,
			created DATETIME,
			type TEXT"""
		order = """
			id INTEGER PRIMARY KEY,
			name TEXT,
			created DATETIME,
			user_id INTEGER,
			status TEXT,
			assinged_designer_id TEXT,
			priority INTEGER,
			quantity INTEGER,
			conditions TEXT,
			comment TEXT,
			color_id INTEGER,
			support_remover TEXT,
			sketches TEXT,
			model_file TEXT,
			plastic_type TEXT,
			printer_type TEXT,
			weight DECIMAL,
			time DECIMAL,
			completion_date DATE,
			start_datetime DATETIME,
			support_time DECIMAL,
			layer_hight DECIMAL,
			price DECIMAL,
			pay_code INTEGER,
			payed DECIMAL,
			prepayment_percent DECIMAL,
			booked TEXT,
			booked_time INTEGER,
			delivery_code INTEGER,
			delivery_user_id INTEGER """
		setting = """
			id INTEGER,
			name TEXT PRIMARY KEY,
			value TEXT"""

		create = 'CREATE TABLE IF NOT EXISTS '
		
		self.cursor.execute(create + 'chat (' + chat + ')')
		self.cursor.execute(create + 'container (' + container + ')')
		self.cursor.execute(create + 'dryer (' + dryer + ')')
		self.cursor.execute(create + 'extruder (' + extruder + ')')
		self.cursor.execute(create + 'location (' + location + ')')
		self.cursor.execute(create + 'printer_type (' + printer_type + ')')
		self.cursor.execute(create + 'printer (' + printer + ')')
		self.cursor.execute(create + 'spool (' + spool + ')')
		self.cursor.execute(create + 'color (' + color + ')')
		self.cursor.execute(create + 'surface (' + surface + ')')
		self.cursor.execute(create + 'order_ (' + order + ')')
		self.cursor.execute(create + 'setting (' + setting + ')')
		self.db.commit()

#---------------------------- LOGIC ----------------------------

	def string_to_date(self, date):
		if date and date != 'None':
			return datetime.strptime(date, '%Y-%m-%d').date()
		else:
			return None

	def string_to_datetime(self, date):
		if date and date != 'None':
			return datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
		else:
			return None

#---------------------------- CHAT ----------------------------

	def get_chats(self):
		self.cursor.execute('SELECT * FROM chat')
		for row in self.cursor.fetchall():
			chat = Chat(self.app, int(row[0]), row[2], bool(row[3]), row[1])
			if row[3]: # employee
				chat.user.roles = row[4].split(',')
				while ('' in chat.user.roles):
   					chat.user.roles.remove("")
			else:
				chat.user.payId = row[5]
				chat.user.money_payed = float(row[6])
				chat.user.orders_canceled = int(row[8])
				chat.user.limit_date = self.string_to_date(row[9])
				chat.last_access_date = self.string_to_date(row[7])
			self.app.chats.append(chat)

	def create_chat(self, chat):
		self.cursor.execute('INSERT OR IGNORE INTO chat VALUES (?,?,"",0,"","",0,"",0,"")', (str(chat.user_id), date.today()))
		self.db.commit()
		self.update_chat(chat)

	def update_chat(self, chat):
		values = 'name = "' + chat.user_name + '", '
		values += 'isEmployee = "' + str(chat.is_employee) + '", '
		if chat.is_employee:
			chat.user.roles.append('')
			while ("" in chat.user.roles):
   				chat.user.roles.remove("")
			values += 'roles = "' + ','.join(chat.user.roles) + '" '
		else:
			values += 'payId = "' + chat.user.payId + '", '
			values += 'money_payed = "' + str(chat.user.money_payed) + '", '
			values += 'last_access_date = "' + str(chat.last_access_date) + '", '
			values += 'orders_canceled = "' + str(chat.user.orders_canceled) + '", '
			values += 'limit_date = "' + str(chat.user.limit_date) + '" '
		self.cursor.execute('UPDATE chat SET ' + values + ' WHERE user_id = ' + str(chat.user_id))
		self.db.commit()

	def remove_chat(self, chat):
		self.cursor.execute('DELETE FROM chat WHERE user_id=?', (str(chat.user_id),))
		self.db.commit()

#---------------------------- ORDER ----------------------------

	def get_orders(self):
		self.cursor.execute('SELECT * FROM order_')
		sql = self.cursor.fetchall()
		orders = []
		for line in sql:
			order = Order(self.app, line[0])
			order.name = line[1]
			order.date = self.string_to_datetime(line[2])
			order.user_id = int(line[3])
			order.status = line[4]
			order.assinged_designer_id = line[5]
			order.priority = int(line[6])
			order.quantity = int(line[7])
			order.conditions = line[8]
			order.comment = line[9]
			order.color_id = int(line[10])
			order.support_remover = line[11]
			order.sketches = line[12]
			order.model_file = line[13]
			order.plastic_type = line[14]
			order.printer_type = line[15]
			order.weight = int(line[16])
			order.time = line[17]
			order.completion_date = line[18]
			order.start_datetime = line[19]
			order.support_time = int(line[20])
			order.layer_hight = line[21]
			order.price = int(line[22])
			order.pay_code = 0 if line[23] == '' else int(line[23])
			order.payed = line[24]
			order.prepayment_percent = int(line[25])
			order.booked = ast.literal_eval(line[26])
			order.booked_time = int(line[27])
			order.delivery_code = int(line[28])
			order.delivery_user_id = int(line[29])
			self.app.orders.append(order)

	def create_order(self, order):
		self.cursor.execute('INSERT INTO order_ VALUES (?,?,"",0,"",0,0,0,"","",0,"","","","","",0,0,"","",0,0,0,0,0,0,"[]",0,0,0)', (order.id, datetime.today()))
		self.db.commit()
		self.update_order(order)

	def update_order(self, order):
		values = 'name = "' + order.name + '", '
		values += 'user_id = "' + str(order.user_id) + '", '
		values += 'status = "' + order.status + '", '
		values += 'assinged_designer_id = "' + str(order.assinged_designer_id) + '", '
		values += 'priority = "' + str(order.priority) + '", '
		values += 'quantity = "' + str(order.quantity) + '", '
		values += 'conditions = "' + order.conditions + '", '
		values += 'comment = "' + order.comment + '", '
		values += 'color_id = "' + str(order.color_id) + '", '
		values += 'support_remover = "' + str(order.support_remover) + '", '
		values += 'sketches = "' + str(order.sketches) + '", '
		values += 'model_file = "' + order.model_file + '", '
		values += 'plastic_type = "' + order.plastic_type + '", '
		values += 'printer_type = "' + order.printer_type + '", '
		values += 'weight = "' + str(order.weight) + '", '
		values += 'time = "' + str(order.time) + '", '
		values += 'completion_date = "' + str(order.completion_date) + '", '
		values += 'start_datetime = "' + str(order.start_datetime) + '", '
		values += 'support_time = "' + str(order.support_time) + '", '
		values += 'layer_hight = "' + str(order.layer_hight) + '", '
		values += 'price = "' + str(order.price) + '", '
		values += 'pay_code = "' + str(order.pay_code) + '", '
		values += 'payed = "' + str(order.payed) + '", '
		values += 'prepayment_percent = "' + str(order.prepayment_percent) + '", '
		values += 'booked = "' + str(order.booked) + '", '
		values += 'booked_time = "' + str(order.booked_time) + '", '
		values += 'delivery_code = "' + str(order.delivery_code) + '", '
		values += 'delivery_user_id = "' + str(order.delivery_user_id) + '" '
		self.cursor.execute('UPDATE order_ SET ' + values + ' WHERE id = ' + str(order.id))
		self.db.commit()

	def remove_order(self, order):
		self.cursor.execute('DELETE FROM order_ WHERE id=?', (order.id,))
		self.db.commit()

#---------------------------- EQUIPMENT ----------------------------

	def get_containers(self):
		self.cursor.execute('SELECT * FROM container')
		sql = self.cursor.fetchall()
		for line in sql:
			container = Container(self.app, int(line[0]))
			container.created = self.string_to_date(line[1])
			container.type = line[2]
			container.capacity = int(line[3])
			self.app.equipment.containers.append(container)

	def add_container(self, container):
		self.cursor.execute('INSERT INTO container VALUES (?,?,?,?)', (container.id, date.today(), container.type, container.capacity))
		self.db.commit()

	def remove_container(self, id):
		self.cursor.execute('DELETE FROM container WHERE id=?', (id,))
		self.db.commit()

	def get_dryers(self):
		self.cursor.execute('SELECT * FROM dryer')
		sql = self.cursor.fetchall()
		for line in sql:
			dryer = Dryer(self.app, int(line[0]))
			dryer.created = self.string_to_date(line[1])
			dryer.name = line[2]
			dryer.capacity = line[3]
			dryer.minTemp = line[4]
			dryer.maxTemp = line[5]
			dryer.maxTime = line[6]
			self.app.equipment.dryers.append(dryer)

	def add_dryer(self, dryer):
		self.cursor.execute('INSERT INTO dryer VALUES (?,?,?,?,?,?,?)', (dryer.id, date.today(), dryer.name, dryer.capacity, dryer.minTemp, dryer.maxTemp, dryer.maxTime))
		self.db.commit()

	def remove_dryer(self, id):
		self.cursor.execute('DELETE FROM dryer WHERE id=?', (id,))
		self.db.commit()

	def get_extruders(self):
		self.cursor.execute('SELECT * FROM extruder')
		sql = self.cursor.fetchall()
		for line in sql:
			extruder = Extruder(self.app, int(line[0]))
			extruder.created = self.string_to_date(line[1])
			extruder.name = line[2]
			extruder.maxTemp = line[3]
			extruder.nozzleDiameter = line[4]
			self.app.equipment.extruders.append(extruder)

	def add_extruder(self, extruder):
		self.cursor.execute('INSERT INTO extruder VALUES (?,?,?,?,?)', (extruder.id, date.today(), extruder.name, extruder.maxTemp, extruder.nozzleDiameter))
		self.db.commit()

	def remove_extruder(self, id):
		self.cursor.execute('DELETE FROM extruder WHERE id=?', (id,))
		self.db.commit()

	def get_locations(self):
		self.cursor.execute('SELECT * FROM location')
		sql = self.cursor.fetchall()
		for line in sql:
			location = Location(self.app, int(line[0]))
			location.date = self.string_to_date(line[1])
			location.name = line[2]
			location.type = line[3]
			self.app.equipment.locations.append(location)

	def add_location(self, location):
		self.cursor.execute('INSERT INTO location VALUES (?,?,?,?)', (location.id, date.today(), location.name, location.type))
		self.db.commit()

	def remove_location(self, id):
		self.cursor.execute('DELETE FROM location WHERE id=?', (id,))
		self.db.commit()

	def get_printer_types(self):
		self.cursor.execute('SELECT * FROM printer_type')
		sql = self.cursor.fetchall()
		for line in sql:
			printer_type = Printer_type(self.app, int(line[0]))
			printer_type.name = line[1]
			printer_type.hour_cost = line[2]
			self.app.equipment.printer_types.append(printer_type)

	def add_printer_type(self, printer_type):
		self.cursor.execute('INSERT INTO printer_type VALUES (?,?,?)', (printer_type.id, printer_type.name, printer_type.hour_cost))
		self.db.commit()

	def remove_printer_type(self, id):
		self.cursor.execute('DELETE FROM printer_type WHERE id=?', (id,))
		self.db.commit()

	def get_printers(self):
		self.cursor.execute('SELECT * FROM printer')
		sql = self.cursor.fetchall()
		for line in sql:
			printer = Printer(self.app, int(line[0]))
			printer.date = self.string_to_date(line[1])
			printer.name = line[2]
			printer.type_ = line[3]
			self.app.equipment.printers.append(printer)

	def add_printer(self, printer):
		self.cursor.execute('INSERT INTO printer VALUES (?,?,?,?)', (printer.id, date.today(), printer.name, printer.type_))
		self.db.commit()

	def remove_printer(self, id):
		self.cursor.execute('DELETE FROM printer WHERE id=?', (id,))
		self.db.commit()

	def get_spools(self):
		self.cursor.execute('SELECT * FROM spool')
		sql = self.cursor.fetchall()
		for line in sql:
			spool = Spool(self.app, int(line[0]))
			spool.date = self.string_to_date(line[1])
			spool.type = line[2]
			spool.diameter = float(line[3])
			spool.weight = int(line[4])
			spool.density = float(line[5])
			spool.color_id = int(line[6])
			spool.dried = bool(line[7])
			spool.brand = line[8]
			spool.booked = int(line[9])
			spool.used = int(line[10])
			spool.price = int(line[11])
			spool.status = line[12]
			spool.delivery_date_estimate = self.string_to_date(line[13])
			self.app.equipment.spools.append(spool)

	def add_spool(self, spool):
		self.cursor.execute('INSERT INTO spool VALUES (?,?,"","",0,"",0,0,"",0,0,"","","")', (spool.id, str(spool.date)))
		self.db.commit()
		self.update_spool(spool)

	def update_spool(self, spool):
		values = 'type = "' + spool.type + '", '
		values += 'diameter = "' + str(spool.diameter) + '", '
		values += 'weight = "' + str(spool.weight) + '", '
		values += 'density = "' + str(spool.density) + '", '
		values += 'color_id = "' + str(spool.color_id) + '", '
		values += 'dried = "' + str(spool.dried) + '", '
		values += 'brand = "' + spool.brand + '", '
		values += 'used = "' + str(spool.used) + '", '
		values += 'price = "' + str(spool.price) + '", '
		values += 'status = "' + str(spool.status) + '", '
		values += 'delivery_date_estimate = "' + str(spool.delivery_date_estimate) + '" '
		self.cursor.execute('UPDATE spool SET ' + values + ' WHERE id = ' + str(spool.id))
		self.db.commit()

	def remove_spool(self, id):
		self.cursor.execute('DELETE FROM spool WHERE id=?', (id,))
		self.db.commit()

	def get_colors(self):
		self.cursor.execute('SELECT * FROM color')
		sql = self.cursor.fetchall()
		for line in sql:
			color = Color(self.app, int(line[0]))
			color.date = self.string_to_date(line[1])
			color.name = line[2]
			color.parent = line[3]
			color.samplePhoto = line[4]
			self.app.equipment.colors.append(color)

	def add_color(self, color):
		self.cursor.execute('INSERT INTO color VALUES (?,Null,Null,Null,Null)', (color.id,))
		self.db.commit()
		self.update_color(color)

	def update_color(self, color):
		values = 'created = "' + str(color.date) + '", '
		values += 'name = "' + color.name + '", '
		values += 'parent_id = "' + str(color.parent_id) + '", '
		values += 'samplePhoto = "' + color.samplePhoto + '" '
		self.cursor.execute('UPDATE color SET ' + values + ' WHERE id = ' + str(color.id))
		self.db.commit()

	def remove_color(self, color):
		self.cursor.execute('DELETE FROM color WHERE id=?', (color.id,))
		self.db.commit()
	
	def get_surfaces(self):
		self.cursor.execute('SELECT * FROM surface')
		sql = self.cursor.fetchall()
		for line in sql:
			surfaces = Surface(self.app, int(line[0]))
			surfaces.created = line[1]
			surfaces.type = line[2]

	def add_surface(self, surface):
		self.cursor.execute('INSERT INTO surface VALUES (?,?,?)', (surface.id, date.today(), surface.type))
		self.db.commit()

	def remove_surface(self, id):
		self.cursor.execute('DELETE FROM surface WHERE id=?', (id,))
		self.db.commit()

	def get_settings(self):
		self.cursor.execute('SELECT name, value FROM setting')
		sql = self.cursor.fetchall()
		settings = {}
		for setting in sql:
			settings[setting[0]] = setting[1]
		return settings

	def add_setting(self, name, value):
		self.cursor.execute('INSERT INTO setting VALUES (Null,?,Null)', (name,))
		self.db.commit()
		self.update_setting(name, value)

	def update_setting(self, name, value):
		values = 'value = "' + value + '" '
		self.cursor.execute('UPDATE setting SET ' + values + ' WHERE name = "' + name + '"')
		self.db.commit()

	def remove_setting(self, name):
		self.cursor.execute('DELETE FROM setting WHERE name=?', (name,))
		self.db.commit()