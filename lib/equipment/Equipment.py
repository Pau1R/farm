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
from datetime import date

class Equipment:
	app = None
	db = None

	containers = []
	dryers = []
	extruders = []
	locations = []
	printer_types = []
	printers = []
	spools = []
	spool_logic = None
	color_logic = None
	colors = []
	surfaces = []

	container = None
	dryer = None
	extruder = None
	location = None
	printer = None
	spool = None
	color = None
	surface = None

	def init(self, app, db):
		self.app = app
		self.db = db
		self.db.get_containers()
		self.db.get_dryers()
		self.db.get_extruders()
		self.db.get_locations()
		self.db.get_printer_types()
		self.db.get_printers()
		self.db.get_spools()
		self.db.get_colors()
		self.db.get_surfaces()

		self.sort_containers()
		self.sort_dryers()
		self.sort_extruders()
		self.sort_locations()
		self.sort_printer_types()
		self.sort_printers()
		self.sort_spools()
		self.sort_colors()
		self.sort_surfaces()

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
				self.db.remove_container(container.id)
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
				self.db.remove_dryer(id)
				self.dryers.remove(dryer)
				break

	def sort_dryers(self):
		self.dryers.sort(key=self.get_object_id)

	def create_new_extruder(self, name, maxTemp, nozzle):
		id = self.app.functions.get_next_free_id(self.extruders)
		extruder = Extruder(self.db, id)
		extruder.name = name
		extruder.maxTemp = maxTemp
		extruder.nozzle = nozzle
		self.db.add_extruder(extruder)
		self.extruders.append(extruder)
		return extruder

	def remove_extruder(self, id):
		for extruder in self.extruders:
			if extruder.id == id:
				self.db.remove_extruder(id)
				self.extruders.remove(extruder)
				break

	def sort_extruders(self):
		self.extruders.sort(key=self.get_object_id)

	def create_new_location(self, name, type):
		id = self.app.functions.get_next_free_id(self.locations)
		location = Location(self.db, id)
		location.name = name
		location.type = type
		self.db.add_location(location)
		self.locations.append(location)
		return location

	def remove_location(self, id):
		for location in self.locations:
			if location.id == id:
				self.db.remove_location(id)
				self.locations.remove(location)
				break

	def sort_locations(self):
		self.locations.sort(key=self.get_object_id)

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
				self.db.remove_printer_type(id)
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
				self.db.remove_printer(id)
				self.printers.remove(printer)
				break

	def sort_printers(self):
		self.printers.sort(key=self.get_object_id)

	def print_cost(self, type_):
		for printer in self.printer_types:
			if printer.name == type_:
				return printer.hour_cost
		print('Equipment.py, print_cost: possible error, self.printer_types:', self.printer_types, ', type_:', type_)
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
		spool.booked = booked
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
				self.db.remove_spool(int(id))
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

	def create_new_surface(self, type):
		id = self.app.functions.get_next_free_id(self.surfaces)
		surface = Surface(self.db, id)
		surface.type = type
		self.db.add_surface(surface)
		self.surfaces.append(surface)
		return surface

	def remove_surface(self, id):
		for surface in self.surfaces:
			if surface.id == id:
				self.db.remove_surface(id)
				self.surfaces.remove(surface)
				break

	def sort_surfaces(self):
		self.surfaces.sort(key=self.get_object_id)