from lib.equipment.Container import Container
from lib.equipment.Dryer import Dryer
from lib.equipment.Extruder import Extruder
from lib.equipment.Location import Location
from lib.equipment.Printer import Printer
from lib.equipment.Spool import Spool
from lib.equipment.Surface import Surface
from lib.Database import Database
from lib.equipment.Equipment import Equipment
from lib.Chat import Chat
from datetime import date
from lib.Msg import Message

class Test:
	db = None

	def __init__(self, db):
		self.db = db
		container = Container(self.db, '2', 'dry', 4)
		# self.db.add_container(container)