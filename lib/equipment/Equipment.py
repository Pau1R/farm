from lib.equipment.container.Container import Container
from lib.equipment.dryer.Dryer import Dryer
from lib.equipment.extruder.Extruder import Extruder
from lib.equipment.zone.Zone import Zone
from lib.equipment.printer_type.Printer_type import Printer_type
from lib.equipment.printer.Printer import Printer
from lib.equipment.spool.Spool import Spool
from lib.equipment.spool.Logic import Spool_logic
from lib.equipment.color.Color import Color
from lib.equipment.color.Logic import Color_logic
from lib.equipment.bed.Bed import Bed
from datetime import date

class Equipment:

	def init(self, app, db):
		self.app = app
		self.db = db
		
		self.containers = []
		self.dryers = []
		self.extruders = []
		self.zones = []
		self.printer_types = []
		self.printers = []
		self.spools = []
		self.spool_logic = None
		self.color_logic = None
		self.colors = []
		self.beds = []

		self.container = None
		self.dryer = None
		self.extruder = None
		self.zone = None
		self.printer = None
		self.spool = None
		self.color = None
		self.bed = None

		self.db.get_containers()
		self.db.get_dryers()
		self.db.get_extruders()
		self.db.get_zones()
		self.db.get_printer_types()
		self.db.get_printers()
		self.db.get_spools()
		self.db.get_colors()
		self.db.get_beds()

		self.sort_containers()
		self.sort_dryers()
		self.sort_extruders()
		self.sort_zones()
		self.sort_printer_types()
		self.sort_printers()
		self.sort_spools()
		self.sort_colors()
		self.sort_beds()

		self.color_logic = Color_logic(app)
		self.spool_logic = Spool_logic(app)

	def get_object_id(self, element):
		return element.id

	def create_new_container(self, type, capacity):
		id = self.app.functions.get_next_free_id(self.containers)
		container = Container(self.app, id)
		container.type = type
		container.capacity = capacity
		self.db.add_container(container)
		self.containers.append(container)
		self.sort_containers()
		return container

	def remove_container(self, id):
		for container in self.containers:
			if container.id == id:
				self.db.remove_container(container)
				self.containers.remove(container)
				break

	def sort_containers(self):
		self.containers.sort(key=self.get_object_id)

	def create_new_dryer(self, name, capacity, minTemp, maxTemp, maxTime):
		id = self.app.functions.get_next_free_id(self.dryers)
		dryer = Dryer(self.app, id)
		dryer.name = name
		dryer.capacity = capacity
		dryer.minTemp = minTemp
		dryer.maxTemp = maxTemp
		dryer.maxTime = maxTime
		self.db.add_dryer(dryer)
		self.dryers.append(dryer)
		self.sort_dryers()
		return dryer

	def remove_dryer(self, id):
		for dryer in self.dryers:
			if dryer.id == id:
				self.db.remove_dryer(dryer)
				self.dryers.remove(dryer)
				break

	def sort_dryers(self):
		self.dryers.sort(key=self.get_object_id)
		self.dryers.sort(key=self.get_object_id)

	def create_new_extruder(self, name, maxTemp, nozzle):
		id = self.app.functions.get_next_free_id(self.extruders)
		extruder = Extruder(self.db, id)
		extruder.name = name
		extruder.maxTemp = maxTemp
		extruder.nozzleDiameter = nozzle
		self.db.add_extruder(extruder)
		self.extruders.append(extruder)
		return extruder

	def remove_extruder(self, id):
		for extruder in self.extruders:
			if extruder.id == id:
				self.db.remove_extruder(extruder)
				self.extruders.remove(extruder)
				break

	def sort_extruders(self):
		self.extruders.sort(key=self.get_object_id)

	def create_new_zone(self, name, type):
		id = self.app.functions.get_next_free_id(self.zones)
		zone = Zone(self.db, id)
		zone.name = name
		zone.type = type
		self.db.add_zone(zone)
		self.zones.append(zone)
		return zone

	def remove_zone(self, id):
		for zone in self.zones:
			if zone.id == id:
				self.db.remove_zone(zone)
				self.zones.remove(zone)
				break

	def sort_zones(self):
		self.zones.sort(key=self.get_object_id)

	def create_new_printer_type(self, name, hour_cost):
		id = self.app.functions.get_next_free_id(self.printer_types)
		printer_type = Printer_type(self.app, id)
		printer_type.name = name
		printer_type.hour_cost = hour_cost
		self.db.add_printer_type(printer_type)
		self.printer_types.append(printer_type)
		return printer_type

	def remove_printer_type(self, id):
		for printer_type in self.printer_types:
			if printer_type.id == id:
				self.db.remove_printer_type(printer_type)
				self.printer_types.remove(printer_type)
				break

	def sort_printer_types(self):
		self.printer_types.sort(key=self.get_object_id)

	def create_new_printer(self, name, type_):
		id = self.app.functions.get_next_free_id(self.printers)
		printer = Printer(self.app, id)
		printer.name = name
		printer.type_ = type_
		self.db.add_printer(printer)
		self.printers.append(printer)
		return printer

	def remove_printer(self, id):
		for printer in self.printers:
			if printer.id == id:
				self.db.remove_printer(printer)
				self.printers.remove(printer)
				break

	def sort_printers(self):
		self.printers.sort(key=self.get_object_id)

	def printer_cost(self, id):
		for printer_type in self.printer_types:
			if printer_type.id == int(id):
				return printer_type.hour_cost
		print('Equipment.py, print_cost: possible error, self.printer_types:', self.printer_types, ', id:', id)
		return None

	def create_new_spool(self, type, diameter, weight, density, color_id, dried, brand, used, price, status, delivery_date_estimate):
		id = self.app.functions.get_next_free_id(self.spools)
		spool = Spool(self.app, id)
		spool.type = type
		spool.diameter = diameter
		spool.weight = weight
		spool.density = density
		spool.color_id = color_id
		spool.dried = dried
		spool.brand = brand
		spool.used = used
		spool.price = price
		spool.status = status
		spool.delivery_date_estimate = delivery_date_estimate

		self.db.add_spool(spool)
		self.spools.append(spool)
		return spool

	def remove_spool(self, id):
		for spool in self.spools:
			if spool.id == int(id):
				self.db.remove_spool(spool)
				self.spools.remove(spool)
				break

	def sort_spools(self):
		self.spools.sort(key=self.get_object_id)

	def create_new_color(self, name, parent_id, samplePhoto):
		id = self.app.functions.get_next_free_id(self.colors)
		color = Color(self.app, id)
		color.name = name
		color.parent_id = parent_id
		color.samplePhoto = samplePhoto
		self.db.add_color(color)
		self.colors.append(color)
		return color

	def sort_colors(self):
		self.colors.sort(key=self.get_object_id)

	def create_new_bed(self, type):
		id = self.app.functions.get_next_free_id(self.beds)
		bed = Bed(self.db, id)
		bed.type = type
		self.db.add_bed(bed)
		self.beds.append(bed)
		return bed

	def remove_bed(self, id):
		for bed in self.beds:
			if bed.id == id:
				self.db.remove_bed(bed)
				self.beds.remove(bed)
				break

	def sort_beds(self):
		self.beds.sort(key=self.get_object_id)