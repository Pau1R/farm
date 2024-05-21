from lib.equipment.Container import Container
from lib.equipment.Dryer import Dryer
from lib.equipment.Extruder import Extruder
from lib.equipment.Location import Location
from lib.equipment.Printer_type import Printer_type
from lib.equipment.Printer import Printer
from lib.equipment.Spool import Spool
from lib.equipment.Color import Color
from lib.equipment.Surface import Surface
from datetime import date

class Equipment:
	db = None

	equipments = []

	containers = []
	dryers = []
	extruders = []
	locations = []
	printer_types = []
	printers = []
	spools = []
	colors = []
	surfaces = []

	# equipment = None

	container = None
	dryer = None
	extruder = None
	location = None
	printer = None
	spool = None
	color = None
	surface = None

	def init(self, db):
		self.db = db
		for data in self.db.get_containers():
			container = Container(self.db, data[0], data[1], data[2], data[3])
			self.containers.append(container)
		for data in self.db.get_dryers():
			dryer = Dryer(self.db, data[0], data[1], data[2], data[3], data[4], data[5], data[6])
			self.dryers.append(dryer)
		for data in self.db.get_extruders():
			extruder = Extruder(self.db, data[0], data[1], data[2], data[3], data[4])
			self.extruders.append(extruder)
		for data in self.db.get_locations():
			location = Location(self.db, data[0], data[1], data[2], data[3])
			self.locations.append(location)
		for data in self.db.get_printer_types():
			printer_type = Printer_type(self.db, data[0], data[1], data[2])
			self.printer_types.append(printer_type)
		for data in self.db.get_printers():
			printer = Printer(self.db, data[0], data[1], data[2], data[3])
			self.printers.append(printer)
		for data in self.db.get_spools():
			spool = Spool(self.db, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9])
			self.spools.append(spool)
		for data in self.db.get_colors():
			color = Color(self.db, data[0], data[1], data[2], data[3], data[4])
			self.colors.append(color)
		for data in self.db.get_surfaces():
			surface = Surface(self.db, data[0], data[1], data[2])
			self.surfaces.append(surface)
		
		self.sort_containers()
		self.sort_dryers()
		self.sort_extruders()
		self.sort_locations()
		self.sort_printer_types()
		self.sort_printers()
		self.sort_spools()
		self.sort_colors()
		self.sort_surfaces()

	def get_next_free_id(self, equipment):
		ids = []
		for elem in equipment:
			ids.append(int(elem.id))
		ids.sort()
		id = 1
		for elem in ids:
			if elem == id:
				id += 1
			else:
				break
		return str(id)

	def get_object_id(self, element):
		    return element.id

	def create_new_container(self, type, capacity):
		id = self.get_next_free_id(self.containers)
		container = Container(self.db, id, date.today(), type, capacity)
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
		id = self.get_next_free_id(self.dryers)
		dryer = Dryer(self.db, id, date.today(), name, capacity, minTemp, maxTemp, maxTime)
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
		id = self.get_next_free_id(self.extruders)
		extruder = Extruder(self.db, id, date.today(), name, maxTemp, nozzle)
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
		id = self.get_next_free_id(self.locations)
		location = Location(self.db, id, date.today(), name, type)
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
		id = self.get_next_free_id(self.printer_types)
		printer_type = Printer_type(self.db, id, name, hour_cost)
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
		id = self.get_next_free_id(self.printers)
		printer = Printer(self.db, id, date.today(), name, type_)
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

	def create_new_spool(self, type, diameter, weight, density, color, dried, brand, used):
		id = self.get_next_free_id(self.spools)
		spool = Spool(self.db, id, date.today(), type, diameter, weight, density, color, dried, brand, used)
		self.db.add_spool(spool)
		self.spools.append(spool)
		return spool

	def remove_spool(self, id):
		for spool in self.spools:
			if spool.id == id:
				self.db.remove_spool(id)
				self.spools.remove(spool)
				break

	def sort_spools(self):
		self.spools.sort(key=self.get_object_id)

	def available_spools(self):
		diction = {}
		for spool in self.spools:
			if spool.type not in diction:
				# add spool type
				diction[spool.type] = {spool.color: ''}
			else:
				# add spool color
				if spool.color not in diction[spool.type]:
					mini = diction[spool.type].copy()
					mini.update({spool.color: ''})
			# add spool weight
			mini = diction[spool.type]
			if spool.color in mini:
				previous_weight = mini[spool.color]
				if previous_weight == '':
					previous_weight = 0
			mini.update({spool.color: previous_weight + spool.weight})
		return diction

	def spools_average_price(self, material):
		price = 1
		weight = 1
		for spool in self.spools:
			if material == 'Любой' or spool.type == material:
				price += spool.price
				weight += spool.weight
		return int(price/weight)

	def create_new_color(self, name, parent, samplePhoto):
		id = self.get_next_free_id(self.colors)
		color = Color(self.db, id, date.today(), name, parent, samplePhoto)
		self.db.add_color(color)
		self.colors.append(color)
		return color

	def sort_colors(self):
		self.colors.sort(key=self.get_object_id)

	def create_new_surface(self, type):
		id = self.get_next_free_id(self.surfaces)
		surface = Surface(self.db, id, date.today(), type)
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