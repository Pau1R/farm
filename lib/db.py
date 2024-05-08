import sqlite3
from datetime import datetime

class FarmDB:
    db = None
    cursor = None

    appRoot = "/farm"
    dbPath = appRoot + '/farm.db'
    sketchPath = appRoot + "/sketch"
    stlPath = appRoot + "/stl"

    def __init__(self):
        self.connect()

    def connect(self):
    	if not os.path.exists(dbPath):
            os.create(dbPath)
        self.db = sqlite3.connect(dbPath, check_same_thread=False)
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS employee (id INTEGER PRIMARY KEY, created DATETIME, telegramId INTEGER, roles TEXT, name TEXT, removed BOOLEAN)")
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS printer (id INTEGER PRIMARY KEY, created DATETIME, status TEXT, spoolId INTEGER, surfaceId INTEGER, extruderId INTEGER, printId INTEGER, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS extruder (id INTEGER PRIMARY KEY, created DATETIME, status TEXT, lastSpoolId INTEGER, nozzleId INTEGER, maxTemp INTEGER, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS nozzle (id INTEGER PRIMARY KEY, created DATETIME, type TEXT, diameter DECIMAL, material DECIMAL, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS surface (id INTEGER PRIMARY KEY, created DATETIME, type TEXT, refreshedPrintsCount INTEGER, surfaceRefresh DATETIME, printsCount INTEGER, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS dryer (id INTEGER PRIMARY KEY, created DATETIME, status TEXT, loadedSpools TEXT, startTime DATETIME, endTime DATETIME, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS location (id INTEGER PRIMARY KEY, created DATETIME, type TEXT, targetId INTEGER, removed BOOLEAN)")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS client (id INTEGER PRIMARY KEY, created DATETIME, telegramId INTEGER, payId INTEGER, balance INTEGER, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS order (id INTEGER PRIMARY KEY, created DATETIME, clientId INTEGER, quantity INTEGER, plasticType TEXT, plasticColor TEXT, layerHeight DECIMAL, quality TEXT, priority INTEGER, startEstimate DATETIME, readyEstimate DATETIME, priceEstimate INTEGER, price INTEGER, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS model (id INTEGER PRIMARY KEY, created DATETIME, orderId INTEGER, sketchExists TEXT, stlExists TEXT, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS print (id INTEGER PRIMARY KEY, created DATETIME, printerId INTEGER, extruderId INTEGER, modelID INTEGER, timelapse TEXT, printStart DATETIME, printEnd DATETIME, completed BOOLEAN, failed BOOLEAN, removed BOOLEAN)")
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS spool (id INTEGER PRIMARY KEY, created DATETIME, locationId INTEGER, plasticId INTEGER, color TEXT, cost INTEGER, dried DATETIME, driedTime INTEGER, weight INTEGER, diameter DECIMAL, usedLength DECIMAL, brand TEXT, shop TEXT, removed BOOLEAN)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS plastic (id INTEGER PRIMARY KEY, created DATETIME, type TEXT, parentId INTEGER, dryTemp INTEGER, dryTime INTEGER, meltTemp INTEGER, glassTemp, INTEGER, printTemp INTEGER, ambientTemp TEXT, density DECIMAL, surfaceType TEXT, surfaceAdhesion TEXT, shrinkage DECIMAL, removed BOOLEAN)")

        self.db.commit()

# ---ADD-REMOVE------------------------------------------------------------------------------------------------------
    def add_printer(self, status):
    	# set created time and status in printer table

    def remove_printer(self, printerId):
    	# set printer.removed to TRUE

    def add_extruder(self, status, maxTemp):
    	# set created time, status and maxTemp in extruder table

    def remove_extruder(self, extruderId):
    	# set extruder.removed to TRUE
    
    def add_nozzle(self, type, diameter, material):
    	# set created time, type, diameter and material in nozzle table

    def remove_nozzle(self, nozzleId):
    	# set nozzle.removed to TRUE

    def add_surface(self, type):
    	# set created time, type, printsCount=0, surfaceRefresh and refreshedPrintsCount=0 in surface table

    def remove_surface(self, surfaceId):
    	# set surface.removed to TRUE

    def add_dryer(self, status):
    	# set created time and status in dryer table

    def remove_dryer(self, dryerId):
		# set dryer.removed to TRUE

    def add_location(self, type, targetId):
    	# set created time, type and targetId in location table

    def remove_location(self, locationId):
    	# set location.removed to TRUE

# ---ADD-REMOVE------------------------------------------------------------------------------------------------------
    def add_client(self, telegram_id):
    	# set created time, telegramId and payId for client table

    def remove_client(self, clientId):
    	# set client.removed to TRUE

    def add_order(self, clientId)
		# set created time, clientId and priority=0 for order table

	def remove_order(self, orderId):
		# set order.removed to TRUE

	def add_model(self, orderId):
		# set created time and orderId for model table.

	def remove_model(self, modelId):
		# set model.removed to TRUE

	def add_print(self, modelId)
		# set created time and modelID for print table.

	def remove_print(self, printId):
		# set print.removed to TRUE

# ---ADD-REMOVE---------------------------------------------------------------------------------------------------
    def add_spool(self, plasticId, color, cost, weight, diameter, brand, shop):
    	# set created time, plasticId, color, cost, weight, diameter, usedLength=0, brand and shop for spool table

    def remove_spool(self, spoolId):
    	# set spool.removed to TRUE

    def add_plastic(self, type, parentID):
    	# set created time, type and parentID for plastic table

    def remove_plastic(self, plasticId):
    	# set plastic.removed to TRUE

# ---UPDATE-------------------------------------------------------------------------------------------------
	def update_order_plasticType(self, orderId, plasticType):

	def update_order_plasticColor(self, orderId, plasticColor):

	def update_order_layerHeight(self, orderId, layerHeight):

	def update_order_quality(self, orderId, quality):

	def update_order_quantity(self, orderId, quantity):

# ---UPDATE-------------------------------------------------------------------------------------------------
	def update_model_sketchExists(self, modelID, sketchExists):

	def update_model_stlExists(self, modelID, stlExists):

# ---UPDATE-------------------------------------------------------------------------------------------------
	def update_print_printerId(self, printId, printerId):

	def update_print_extruderId(self, printId, extruderId):

# ---UPDATE-------------------------------------------------------------------------------------------------
	def update_spool_location(self, spoolId, locationId):

	def update_spool_dried(self, spoolId, dried):

# ---UPDATE-------------------------------------------------------------------------------------------------
	def update_plastic_dryTemp(self, dryTemp):

	def update_plastic_dryTime(self, dryTime):

	def update_plastic_meltTemp(self, meltTemp):

	def update_plastic_glassTemp(self, glassTemp):

	def update_plastic_printTemp(self, printTemp):

	def update_plastic_ambientTemp(self, ambientTemp):

	def update_plastic_density(self, density):

	def update_plastic_surfaceType(self, surfaceType):

	def update_plastic_surfaceAdhesion(self, surfaceAdhesion):

	def update_plastic_shrinkage(self, shrinkage):

# ---UPDATE-------------------------------------------------------------------------------------------------
	def update_dryer_status(self, status):
		# dryer.status = {working, standby, broken, removed}

	def add_spool_to_dryer(self, spoolId):
		# add spoolId to dryer.loadedSpools
		# update_spool_location() to dryer.

	def remove_spool_from_dryer(self, spoolId):
		# remove spoolId to dryer.loadedSpools
		# set spool.dried to current date.
		# count time spool was in dryer. Add it to spool.driedTime.
		# update_spool_location() to dry box.

	def set_dryer_time(self, startTime, endTime):
		# set dryer.startTime and dryer.endTime

	


# new spools:
# - add_spool()
# - update_spool_location()

# new plastic type:
# - add_plastic()
# update each value of plastic:
# - update_plastic_{setting}

# move spool to :
# -