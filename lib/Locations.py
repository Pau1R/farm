class Locations:
	def __init__(self, app):
		self.app = app

		self.printer_locations = ['zone']
		self.container_locations = ['zone']
		self.dryer_locations = ['zone']
		self.spool_locations = ['zone','container','printer','dryer']
		self.bed_locations = ['zone','printer']

	def get_location(self, type_, id): # specific location
		id = int(id)
		if type_ == 'zone':
			return Zone(self.app, id)
		elif type_ == 'container':
			return Container_(self.app, id)
		elif type_ == 'printer':
			return Printer(self.app, id)
		elif type_ == 'dryer':
			return Dryer(self.app, id)
		else:
			return ''

	def content(self, everything, location_type, location_id):
		contents = []
		for thing in everything:
			if thing.location_type == location_type and thing.location == location_id:
				contents.append(thing)
		return contents

#---------------------------- BUTTONS ----------------------------

	def get_buttons(self, location_type): # locations of specific type
		location_mapping = {
			'zone': self.app.equipment.zones,
			'container': self.app.equipment.containers,
			'printer': self.app.equipment.printers,
			'dryer': self.app.equipment.dryers
		}
		text_formatting = {
			'zone': lambda loc: f'{loc.id}: {loc.name} ({loc.type})',
			'container': lambda loc: f'{loc.id}: {loc.type}',
			'printer': lambda loc: f'{loc.id}: {loc.type().name}',
			'dryer': lambda loc: f'{loc.id}'
		}
		locations = location_mapping.get(location_type, [])
		buttons = [[text_formatting[location_type](location), location.id] for location in locations]
		return buttons

#---------------------------- CLASSES ----------------------------

class Printer:
	def __init__(self, app, id):
		self.app = app
		self.spools = self.app.locations.content(self.app.equipment.spools, 'printer', id)
		self.bed = self.app.locations.content(self.app.equipment.beds, 'printer', id)
	
	def readable_content(self):
		text = ''
		if self.bed:
			text = f'поверхность {self.bed.type}\n'
		if self.spools:
			if len(self.spools) > 1:
				text += 'катушки: '
			else:
				text += 'катушка '
			text += ', '.join(map(str, [spool.id for spool in self.spools]))
		return text.rstrip('\n')

	def empty(self):
		return not (self.spools or self.bed)

class Container_:
	def __init__(self, app, id):
		self.app = app
		self.spools = self.app.locations.content(self.app.equipment.spools, 'container', id)

	def readable_content(self):
		if self.spools:
			text = 'катушка '
			if len(self.spools) > 1:
				text = 'катушки: '
			text += ', '.join(map(str, [spool.id for spool in self.spools]))
		return text.rstrip('\n')

	def empty(self):
		return not self.spools

class Zone:
	def __init__(self, app, id):
		self.app = app

		self.printers = self.app.locations.content(self.app.equipment.printers, 'zone', id)
		self.containers = self.app.locations.content(self.app.equipment.containers, 'zone', id)
		self.dryers = self.app.locations.content(self.app.equipment.dryers, 'zone', id)
		self.spools = self.app.locations.content(self.app.equipment.spools, 'zone', id)
		self.beds = self.app.locations.content(self.app.equipment.beds, 'zone', id)

	def readable_content(self):
		text = ''
		if self.printers:
			text += 'принтер '
			if len(self.spools) > 1:
				text = 'принтеры: '
			text += ', '.join(map(str, [printer.id for printer in self.printers])) + '\n'
		if self.containers:
			text += 'ящик '
			if len(self.containers) > 1:
				text = 'ящики: '
			text += ', '.join(map(str, [container.id for container in self.containers])) + '\n'
		if self.dryers:
			text += 'сушилка '
			if len(self.dryers) > 1:
				text = 'сушилки: '
			text += ', '.join(map(str, [dryer.id for dryer in self.dryers])) + '\n'
		if self.spools:
			text += 'катушка '
			if len(self.spools) > 1:
				text = 'катушки: '
			text += ', '.join(map(str, [spool.id for spool in self.spools])) + '\n'
		if self.beds:
			text += 'поверхности '
			if len(self.beds) > 1:
				text = 'поверхности: '
			text += ', '.join(map(str, [bed.id for bed in self.beds])) + '\n'
		return text.rstrip('\n')

	def empty(self):
		return not (self.printers or self.containers or self.dryers or self.spools or self.beds)

class Dryer:
	def __init__(self, app, id):
		self.app = app
		self.spools = self.app.locations.content(self.app.equipment.spools, 'dryer', id)

	def readable_content(self):
		if self.spools:
			text = 'катушка '
			if len(self.spools) > 1:
				text = 'катушки: '
			text += ', '.join(map(str, [spool.id for spool in self.spools])) + '\n'
		return text.rstrip('\n')
	
	def empty(self):
		return not self.spools
