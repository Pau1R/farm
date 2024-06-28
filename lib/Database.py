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

	def __init__(self, app):
		self.app = app
		self.meta = Meta()
		self.db = None
		self.cursor = None

		self.connect()
		self.edit_database()

	def connect(self):
		appRoot = os.getcwd()
		# appRoot = '/farm'
		dbPath = appRoot + '/farm.db'
		if not os.path.exists(appRoot):
			os.mkdir(self.appRoot)
		self.db = sqlite3.connect(dbPath, check_same_thread=False)
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

#---------------------------- GET DATA ----------------------------

	def get_meta(self, table):
		self.cursor.execute(f'SELECT * FROM "{table}"')
		return [col[0] for col in self.cursor.description]

	def get_row(self, table, columns, row):
		data = {}
		for field, field_type in getattr(Meta, table).items():
			field_type = field_type.split()[0]
			if field in columns:
				index = columns.index(field)
				value = row[index]
				if value is None or value == "None":
					if field_type == "TEXT":
						value = ''
					elif field_type == "LOGICAL":
						value = False
					elif field_type == "DECIMAL":
						value = 0.0
					elif field_type == "INTEGER":
						value = 0
					elif field_type in ["DATETIME","DATE"]:
						value = None
					data[field] = value
				else:
					if field_type == "LOGICAL":
						value = bool(value)
					elif field_type == "DECIMAL":
						value = float(value)
					elif field_type == "INTEGER":
						value = int(value)
					elif field_type in ["DATETIME","DATE"]:
						value = self.string_to_datetime(value)
					data[field] = value
		return data

	def get_table(self, table):
		class_name = table[:1].upper() + table[1:]
		# try:
		Class = globals()[class_name]
		# catch:
			# x = ''
		objects = []
		full_data = []
		columns = self.get_meta(table)
		for row in self.cursor.fetchall():
			data = self.get_row(table, columns, row)
			params = list(inspect.signature(Class.__init__).parameters.keys())[1:]  # get constructer parameters to clear up data
			data_trimmed = {key: data[key] for key in params if key in data}
			obj = Class(self.app, **data_trimmed)
			objects.append(obj)
			full_data.append(data)
		return objects, full_data

#---------------------------- SET DATA ----------------------------

	def create_table_row(self, meta, contents):
		placeholders = f"({', '.join('?' for _ in contents)})"
		self.cursor.execute(f'INSERT OR IGNORE INTO {meta} VALUES {placeholders}', contents)
		self.db.commit()

	def update_table(self, name, contents):
		fields = vars(contents)
		data_fields = getattr(Meta, name)
		formatted_fields = {key: str(value) for key, value in fields.items() if key in data_fields}
		values = ', '.join([f"{key} = ?" for key in formatted_fields.keys()])
		sql_query = f'UPDATE "{name}" SET {values} WHERE id = ?'
		self.cursor.execute(sql_query, list(formatted_fields.values()) + [contents.id])
		self.db.commit()

#---------------------------- LOGIC ----------------------------

	def string_to_date(self, date):
		if date and date != 'None':
			return datetime.strptime(date, '%Y-%m-%d').date()
		else:
			return None

	def string_to_datetime(self, date):
		if date and date != 'None':
			try:
				return datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
			except:
				return datetime.strptime(date, '%Y-%m-%d').date()
		else:
			return None

#---------------------------- CHAT ----------------------------

	def get_chats(self):
		chats, full_data = self.get_table('chat')
		for chat, data in zip(chats, full_data):
			if data['isEmployee']:
				chat.user.roles = [role for role in data['roles'].split(',') if role.strip()]
			else:
				chat.user.payId = data['payId']
				chat.user.money_payed = data['money_payed']
				chat.user.orders_canceled = data['orders_canceled']
				chat.user.limit_date = data['limit_date']
			chat.last_access_date = data['last_access_date']
			self.app.chats.append(chat)

	def create_chat(self, chat):
		self.create_table_row('chat (user_id, created)', (str(chat.user_id), date.today()))
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

	def get_orders(self):
		orders, full_data = self.get_table('order')
		for order, data in zip(orders, full_data):
			order.name = data['name']
			order.created = data['created']
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
			order.completion_date = data['completion_date']
			order.start_datetime = data['start_datetime']
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
		self.create_table_row('order (id, created)', (order.id, order.created))
		self.update_order(order)

	def update_order(self, order):
		self.update_table('order', order)

	def remove_order(self, order):
		self.cursor.execute('DELETE FROM order WHERE id=?', (order.id,))
		self.db.commit()

	def get_gcodes(self):
		gcodes, full_data = self.get_table('gcode')
		for gcode, data in zip(gcodes, full_data):
			gcode.order_id = data['order_id']
			gcode.file_id = data['file_id']
			gcode.screenshot = data['screenshot']
			gcode.status = data['status']
			gcode.duration = data['duration']
			self.app.gcodes.append(gcode)

	def create_gcode(self, gcode):
		self.create_table_row('gcode (id)', (gcode.id,))
		self.update_gcode(gcode)

	def update_gcode(self, gcode):
		self.update_table('gcode', gcode)

	def remove_gcode(self, gcode):
		self.cursor.execute('DELETE FROM gcode WHERE id=?', (gcode.id,))
		self.db.commit()

#---------------------------- EQUIPMENT ----------------------------

	def get_containers(self):
		containers, full_data = self.get_table('container')
		for container, data in zip(containers, full_data):
			container.created = data['created']
			container.type = data['type']
			container.capacity = data['capacity']
			self.app.equipment.containers.append(container)

	def add_container(self, container):
		self.create_table_row('container (id)', (container.id,))
		self.update_container(container)

	def update_container(self, container):
		self.update_table('container', container)

	def remove_container(self, container):
		self.cursor.execute('DELETE FROM container WHERE id=?', (container.id,))
		self.db.commit()

	def get_dryers(self):
		dryers, full_data = self.get_table('dryer')
		for dryer, data in zip(dryers, full_data):
			dryer.created = data['created']
			dryer.name = data['name']
			dryer.capacity = data['capacity']
			dryer.minTemp = data['minTemp']
			dryer.maxTemp = data['maxTemp']
			dryer.maxTime = data['maxTime']
			self.app.equipment.dryers.append(dryer)

	def add_dryer(self, dryer):
		self.create_table_row('dryer (id)', (dryer.id,))
		self.update_dryer(dryer)

	def update_dryer(self, dryer):
		self.update_table('dryer', dryer)

	def remove_dryer(self, dryer):
		self.cursor.execute('DELETE FROM dryer WHERE id=?', (dryer.id,))
		self.db.commit()

	def get_extruders(self):
		extruders, full_data = self.get_table('extruder')
		for extruder, data in zip(extruders, full_data):
			extruder.created = data['created']
			extruder.name = data['name']
			extruder.maxTemp = data['maxTemp']
			extruder.nozzleDiameter = data['nozzleDiameter']
			self.app.equipment.extruders.append(extruder)

	def add_extruder(self, extruder):
		self.create_table_row('extruder (id)', (extruder.id,))
		self.update_extruder(extruder)

	def update_extruder(self, extruder):
		self.update_table('extruder', extruder)

	def remove_extruder(self, extruder):
		self.cursor.execute('DELETE FROM extruder WHERE id=?', (extruder.id,))
		self.db.commit()

	def get_locations(self):
		locations, full_data = self.get_table('location')
		for location, data in zip(locations, full_data):
			location.created = data['created']
			location.name = data['name']
			location.type = data['type']
			self.app.equipment.locations.append(location)

	def add_location(self, location):
		self.create_table_row('location (id)', (location.id,))
		self.update_location(location)

	def update_location(self, location):
		self.update_table('location', location)

	def remove_location(self, location):
		self.cursor.execute('DELETE FROM location WHERE id=?', (location.id,))
		self.db.commit()

	def get_printer_types(self):
		printer_types, full_data = self.get_table('printer_type')
		for printer_type, data in zip(printer_types, full_data):
			printer_type.name = data['name']
			printer_type.hour_cost = data['hour_cost']
			self.app.equipment.printer_types.append(printer_type)

	def add_printer_type(self, printer_type):
		self.create_table_row('printer_type (id)', (printer_type.id,))
		self.update_printer_type(printer_type)

	def update_printer_type(self, printer_type):
		self.update_table('printer_type', printer_type)

	def remove_printer_type(self, printer_type):
		self.cursor.execute('DELETE FROM printer_type WHERE id=?', (printer_type.id,))
		self.db.commit()

	def get_printers(self):
		printers, full_data = self.get_table('printer')
		for printer, data in zip(printers, full_data):
			printer.created = data['created']
			printer.name = data['name']
			printer.type_ = data['type_']
			self.app.equipment.printers.append(printer)

	def add_printer(self, printer):
		self.create_table_row('printer (id)', (printer.id,))
		self.update_printer(printer)

	def update_printer(self, printer):
		self.update_table('printer', printer)

	def remove_printer(self, printer):
		self.cursor.execute('DELETE FROM printer WHERE id=?', (printer.id,))
		self.db.commit()

	def get_spools(self):
		spools, full_data = self.get_table('spool')
		for spool, data in zip(spools, full_data):
			spool.created = data['created']
			spool.type = data['type']
			spool.diameter = data['diameter']
			spool.weight = data['weight']
			spool.density = data['density']
			spool.color_id = data['color_id']
			spool.dried = data['dried']
			spool.brand = data['brand']
			spool.booked = data['booked']
			spool.used = data['used']
			spool.price = data['price']
			spool.status = data['status']
			spool.delivery_date_estimate = data['delivery_date_estimate']
			self.app.equipment.spools.append(spool)

	def add_spool(self, spool):
		self.create_table_row('spool (id)', (spool.id,))
		self.update_spool(spool)

	def update_spool(self, spool):
		self.update_table('spool', spool)

	def remove_spool(self, spool):
		self.cursor.execute('DELETE FROM spool WHERE id=?', (spool.id,))
		self.db.commit()

	def get_colors(self):
		colors, full_data = self.get_table('color')
		for color, data in zip(colors, full_data):
			color.created = data['created']
			color.name = data['name']
			color.parent_id = data['parent_id']
			color.samplePhoto = data['samplePhoto']
			self.app.equipment.colors.append(color)

	def add_color(self, color):
		self.create_table_row('color (id)', (color.id,))
		self.update_color(color)

	def update_color(self, color):
		self.update_table('color', color)

	def remove_color(self, color):
		self.cursor.execute('DELETE FROM color WHERE id=?', (color.id,))
		self.db.commit()
	
	def get_surfaces(self):
		surfaces, full_data = self.get_table('surface')
		for surface, data in zip(surfaces, full_data):
			surface.created = data['created']
			surface.type = data['type']
			self.app.equipment.surfaces.append(surface)

	def add_surface(self, surface):
		self.create_table_row('surface (id)', (surface.id,))
		self.update_surface(surface)

	def update_surface(self, surface):
		self.update_table('surface', surface)

	def remove_surface(self, surface):
		self.cursor.execute('DELETE FROM surface WHERE id=?', (surface.id,))
		self.db.commit()

	def get_settings(self):
		self.cursor.execute('SELECT name, value FROM setting')
		sql = self.cursor.fetchall()
		settings = {}
		for setting in sql:
			settings[setting[0]] = setting[1]
		return settings

	def add_setting(self, name, value):
		self.create_table_row('setting (id)', (setting.id,))
		self.update_setting(setting)

	def update_setting(self, name, value):
		values = 'value = "' + value + '" '
		self.cursor.execute('UPDATE setting SET ' + values + ' WHERE name = "' + name + '"')
		self.db.commit()

	def remove_setting(self, setting):
		self.cursor.execute('DELETE FROM setting WHERE id=?', (setting.id,))
		self.db.commit()

	def get_requests(self):
		requests, full_data = self.get_table('request')
		for request, data in zip(requests, full_data):
			request.user_id = data['user_id']
			request.created = data['created']
			request.text = data['text']
			self.app.requests.append(request)

	def add_request(self, request):
		self.create_table_row('request (id)', (request.id,))
		self.update_request(request)

	def update_request(self, request):
		self.update_table('request', request)

	def remove_request(self, request):
		self.cursor.execute('DELETE FROM request WHERE id=?', (request.id,))
		self.db.commit()