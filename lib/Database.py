import sqlite3
from datetime import date
from datetime import datetime
import os
from lib.Chat import Chat
from lib.Database_meta import Meta
from lib.order.Order import Order
from lib.order.gcode.Gcode import Gcode
from lib.equipment.container.Container import Container
from lib.equipment.dryer.Dryer import Dryer
from lib.equipment.extruder.Extruder import Extruder
from lib.equipment.location.Location import Location
from lib.equipment.printer_type.Printer_type import Printer_type
from lib.equipment.printer.Printer import Printer
from lib.equipment.spool.Spool import Spool
from lib.equipment.spool.Logic import Spool_logic
from lib.equipment.color.Color import Color
from lib.equipment.color.Logic import Color_logic
from lib.equipment.surface.Surface import Surface
from lib.request.Request import Request

import inspect
import time
import ast

class Database:
	app = None
	meta = None

	db = None
	cursor = None

	appRoot = os.getcwd()
	# appRoot = '/farm'
	dbPath = appRoot + '/farm.db'

	def __init__(self, app):
		self.app = app
		self.meta = Meta()

		self.connect()
		self.edit_database()

	def connect(self):
		if not os.path.exists(self.appRoot):
			os.mkdir(self.appRoot)
		self.db = sqlite3.connect(self.dbPath, check_same_thread=False)
		self.cursor = self.db.cursor()

#---------------------------- METADATA EDIT ----------------------------

	def edit_database(self):
		tables = [attr for attr in vars(Meta) if not attr.startswith('__')]

		# create tables
		for table in tables:
			self.create_table(table, getattr(self.meta, table))

		# delete tables
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
		existing_tables = [row[0] for row in self.cursor.fetchall()]
		for table in existing_tables:
			if table not in tables:
				self.cursor.execute(f'DROP TABLE IF EXISTS "{table}";')

	def create_table(self, table_name, table_fields):
		# create table and columns
		columns = ",\n    ".join([f"{col_name} {col_type}" for col_name, col_type in table_fields.items()])
		create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    {columns}\n);'
		self.cursor.execute(create_table_sql)

		# get columns
		self.cursor.execute(f'PRAGMA table_info("{table_name}")')
		existing_columns = {row[1]: row[2] for row in self.cursor.fetchall()}  # Column name to type mapping

		# add columns
		for col_name, col_type in table_fields.items():
			if col_name not in existing_columns:
				alter_table_sql = f'ALTER TABLE "{table_name}" ADD COLUMN {col_name} {col_type};'
				self.cursor.execute(alter_table_sql)
				# set default values for new column
				if col_type in ['TEXT','DATETIME','']:
					self.cursor.execute(f'UPDATE "{table_name}" SET {col_name} = ""')
				elif col_type in ['INTEGER','REAL','LOGICAL','DECIMAL']:
					self.cursor.execute(f'UPDATE "{table_name}" SET {col_name} = 0')

		# delete columns
		for col_name in existing_columns:
			if col_name not in table_fields:
				drop_column_sql = f"ALTER TABLE {table_name} DROP COLUMN {col_name};"
				self.cursor.execute(drop_column_sql)
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

#---------------------------- GET DATA ----------------------------

	def get_meta(self, table):
		self.cursor.execute(f'SELECT * FROM "{table}"')
		return [col[0] for col in self.cursor.description]

	def get_data(self, table, columns, row):
		data = {}
		for field, field_type in getattr(Meta, table).items():
			if field in columns:
				index = columns.index(field)
				value = row[index]
				if value is not None:
					if field_type == "LOGICAL":
						value = bool(value)
					elif field_type == "DECIMAL":
						value = float(value)
					elif field_type == "INTEGER":
						value = int(value)
					elif field_type == "DATETIME":
						value = self.string_to_date(value)
					data[field] = value
		return data

	def get_objects(self, table):
		class_name = table[:1].upper() + table[1:]
		Class = globals()[class_name]
		objects = []
		full_data = []
		columns = self.get_meta(table)
		for row in self.cursor.fetchall():
			data = self.get_data(table, columns, row)
			params = list(inspect.signature(Class.__init__).parameters.keys())[1:]  # get constructer parameters to clear up data
			data_trimmed = {key: data[key] for key in params if key in data}
			obj = Class(self.app, **data_trimmed)
			objects.append(obj)
			full_data.append(data)
		return objects, full_data

#---------------------------- SET DATA ----------------------------

	def update_table(self, name, contents):
		fields = vars(contents)
		data_fields = getattr(Meta, name)
		formatted_fields = {key: str(value) for key, value in fields.items() if key in data_fields}
		values = ', '.join([f"{key} = ?" for key in formatted_fields.keys()])
		sql_query = f'UPDATE "{name}" SET {values} WHERE id = ?'
		self.cursor.execute(sql_query, list(formatted_fields.values()) + [contents.id])
		self.db.commit()

#---------------------------- CHAT ----------------------------

	def get_chats(self):
		chats, full_data = self.get_objects('chat')
		for chat, data in zip(chats, full_data):
			if data['isEmployee']:
				chat.user.roles = [role for role in data['roles'].split(',') if role.strip()]
			else:
				chat.user.payId = data['payId']
				chat.user.money_payed = data['money_payed']
				chat.user.orders_canceled = data['orders_canceled']
				chat.user.limit_date = self.string_to_date(data['limit_date'])
			chat.last_access_date = self.string_to_date(data['last_access_date'])
			self.app.chats.append(chat)

	def create_chat(self, chat):
		self.cursor.execute('INSERT OR IGNORE INTO chat (user_id, created) VALUES (?, ?)', (str(chat.user_id), date.today()))
		self.db.commit()
		self.update_chat(chat)

	def update_chat(self, chat):
		values = 'name = "' + chat.user_name + '", '
		values += 'isEmployee = "' + str(int(chat.is_employee)) + '", '
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


	def get_chats(self):
		chats, full_data = self.get_objects('chat')
		for chat, data in zip(chats, full_data):
			if data['isEmployee']:
				chat.user.roles = [role for role in data['roles'].split(',') if role.strip()]
			else:
				chat.user.payId = data['payId']
				chat.user.money_payed = data['money_payed']
				chat.user.orders_canceled = data['orders_canceled']
				chat.user.limit_date = self.string_to_date(data['limit_date'])
			chat.last_access_date = self.string_to_date(data['last_access_date'])
			self.app.chats.append(chat)


	def get_orders(self):
		orders, full_data = self.get_objects('order')
		for order, data in zip(orders, full_data):
			order.name = data['name']
			order.date = self.string_to_datetime(data['created'])
			order.user_id = data['user_id']
			order.type = data['type']
			order.physical_status = data['physical_status']
			order.logical_status = data['logical_status']
			order.assigned_designer_id = data['assigned_designer_id']
			order.priority = data['priority']
			order.quantity = data['quantity']
			order.quality = data['quality']
			order.comment = data['comment']
			order.color_id = data['color_id']
			order.support_remover = data['support_remover']
			order.sketches = ast.literal_eval(data['sketches'])
			order.model_file = data['model_file']
			order.link = data['link']
			order.design_time = data['design_time']
			order.print_time = data['print_time']
			order.plastic_type = data['plastic_type']
			order.printer_type = data['printer_type']
			order.weight = data['weight']
			order.completion_date = self.string_to_date(data['completion_date'])
			order.start_datetime = self.string_to_datetime(data['start_datetime'])
			order.support_time = data['support_time']
			order.layer_height = data['layer_height']
			order.price = data['price']
			order.pay_code = data['pay_code']
			order.payed = data['payed']
			order.prepayment_percent = data['prepayment_percent']
			order.booked = ast.literal_eval(data['booked'])
			order.booked_time = data['booked_time']
			order.delivery_code = data['delivery_code']
			order.delivery_user_id = data['delivery_user_id']
			self.app.orders.append(order)

	def create_order(self, order):
	    self.cursor.execute('INSERT INTO order (id, created) VALUES (?, ?)', (order.id, order.date))
	    self.db.commit()
	    self.update_order(order)

	def update_order(self, order):
		self.update_table('order', order)

	def remove_order(self, order):
		self.cursor.execute('DELETE FROM order WHERE id=?', (order.id,))
		self.db.commit()



	def get_gcodes(self):
		self.cursor.execute('SELECT * FROM gcode')
		sql = self.cursor.fetchall()
		for line in sql:
			gcode = Gcode(self.app, line[0])
			gcode.order_id = line[1]
			gcode.file_id = line[2]
			gcode.screenshot = line[3]
			gcode.status = line[4]
			gcode.duration = line[5]
			self.app.gcodes.append(gcode)

	def create_gcode(self, gcode):
		self.cursor.execute('INSERT INTO gcode VALUES (?,0,"","","",0)', (gcode.id,))
		self.db.commit()
		self.update_gcode(gcode)

	def update_gcode(self, gcode):
		values = 'order_id = "' + str(gcode.order_id) + '", '
		values += 'file_id = "' + gcode.file_id + '", '
		values += 'screenshot = "' + gcode.screenshot + '", '
		values += 'status = "' + gcode.status + '", '
		values += 'duration = "' + str(gcode.duration) + '" '
		self.cursor.execute('UPDATE gcode SET ' + values + ' WHERE id = ' + str(gcode.id))
		self.db.commit()

	def remove_gcode(self, gcode):
		self.cursor.execute('DELETE FROM gcode WHERE id=?', (gcode.id,))
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
			color.parent_id = int(line[3])
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
			surface = Surface(self.app, int(line[0]))
			surface.created = line[1]
			surface.type = line[2]
			self.app.equipment.surfaces.append(surface)

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

	def get_requests(self):
		self.cursor.execute('SELECT * FROM request')
		sql = self.cursor.fetchall()
		for line in sql:
			request = Request(self.app, int(line[0]))
			request.user_id = int(line[1])
			request.date = self.string_to_date(line[2])
			request.text = line[3]
			self.app.requests.append(request)

	def add_request(self, request):
		self.cursor.execute('INSERT INTO request VALUES (?,?,?,?)', (request.id, request.user_id, date.today(), request.text))
		self.db.commit()

	def remove_request(self, request):
		self.cursor.execute('DELETE FROM request WHERE id=?', (request.id,))
		self.db.commit()