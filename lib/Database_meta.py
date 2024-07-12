# This class should ONLY contain the metaschema for the database as the fields are converted to database structure
# The database is constructed automatically based on this class field names and contents
class Meta:
    chat = {
        "user_id": "INTEGER PRIMARY KEY",
        "created": "DATETIME DEFAULT ''",
        "name": "TEXT DEFAULT ''",
        "isEmployee": "LOGICAL DEFAULT 0",
        "roles": "TEXT DEFAULT ''",
        "payId": "TEXT DEFAULT ''",
        "money_payed": "DECIMAL DEFAULT 0",
        "last_access_date": "DATETIME DEFAULT ''",
        "orders_canceled": "INTEGER DEFAULT 0",
        "limit_date": "DATETIME DEFAULT ''"}
    container = {
        "id": "INTEGER PRIMARY KEY",
        "created": "DATETIME DEFAULT ''",
        "type": "TEXT DEFAULT ''",
        "capacity": "INTEGER DEFAULT 0"}
    dryer = {
        "id": "INTEGER PRIMARY KEY",
        "created": "DATETIME DEFAULT ''",
        "name": "TEXT DEFAULT ''",
        "capacity": "INTEGER DEFAULT 0",
        "minTemp": "INTEGER DEFAULT 0",
        "maxTemp": "INTEGER DEFAULT 0",
        "maxTime": "INTEGER DEFAULT 0"}
    extruder = {
        "id": "INTEGER PRIMARY KEY",
        "created": "DATETIME DEFAULT ''",
        "name": "TEXT DEFAULT ''",
        "maxTemp": "INTEGER DEFAULT 0",
        "nozzleDiameter": "DECIMAL DEFAULT 0"}
    location = {
        "id": "INTEGER PRIMARY KEY",
        "created": "DATETIME DEFAULT ''",
        "name": "TEXT DEFAULT ''",
        "type": "TEXT DEFAULT ''"}
    printer_type = {
        "id": "INTEGER PRIMARY KEY",  
        "name": "TEXT DEFAULT ''",
        "hour_cost": "INTEGER DEFAULT 0"}
    printer = {
        "id": "INTEGER PRIMARY KEY", 
        "created": "DATETIME DEFAULT ''",
        "name": "TEXT DEFAULT ''",
        "type_": "INTEGER DEFAULT 0"}
    spool = {
        "id": "INTEGER PRIMARY KEY",
        "created": "DATETIME DEFAULT ''",
        "type": "TEXT DEFAULT ''",
        "diameter": "DECIMAL DEFAULT 0",
        "weight": "INTEGER DEFAULT ''",
        "density": "DECIMAL DEFAULT 0",
        "color_id": "INTEGER DEFAULT ''",
        "dried": "LOGICAL DEFAULT ''",
        "brand": "TEXT DEFAULT ''",
        "booked": "INTEGER DEFAULT 0",
        "used": "INTEGER DEFAULT ''",
        "price": "INTEGER DEFAULT 0",
        "status": "TEXT DEFAULT ''",
        "delivery_date_estimate": "DATETIME DEFAULT ''"}
    color = {
        "id": "INTEGER PRIMARY KEY",
        "created": "DATETIME DEFAULT ''",
        "name": "TEXT DEFAULT ''",
        "parent_id": "INTEGER DEFAULT 0",
        "samplePhoto": "TEXT DEFAULT ''"}
    surface = {
        "id": "INTEGER PRIMARY KEY",
        "created": "DATETIME DEFAULT ''",
        "type": "TEXT DEFAULT ''"}
    order = {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT DEFAULT ''",
        "created": "DATETIME DEFAULT ''",
        "user_id": "INTEGER DEFAULT 0",
        "type": "TEXT DEFAULT ''",
        "physical_status": "TEXT DEFAULT ''",
        "logical_status": "TEXT DEFAULT ''",
        "designer_id": "INTEGER DEFAULT ''",
        "priority": "INTEGER DEFAULT 0",
        "confirmed": "LOGICAL DEFAULT 1",
        "quantity": "INTEGER DEFAULT 0",
        "quality": "TEXT DEFAULT ''",
        "comment": "TEXT DEFAULT ''",
        "color_id": "INTEGER DEFAULT 0",
        "support_remover": "TEXT DEFAULT ''",
        "sketches": "TEXT DEFAULT '[]'",
        "screenshots": "TEXT DEFAULT '[]'",
        "model_file": "TEXT DEFAULT ''",
        "link": "TEXT DEFAULT ''",
        "design_time": "INTEGER DEFAULT 0",
        "print_time": "INTEGER DEFAULT 0",
        "plastic_type": "TEXT DEFAULT ''",
        "printer_type": "TEXT DEFAULT ''",
        "weight": "DECIMAL DEFAULT 0",
        "completion_date": "DATE DEFAULT ''",
        "start_datetime": "DATETIME DEFAULT ''",
        "support_time": "DECIMAL DEFAULT 0",
        "layer_height": "DECIMAL DEFAULT 0",
        "price": "INTEGER DEFAULT 0",
        "pay_code": "INTEGER DEFAULT 0",
        "payed": "INTEGER DEFAULT 0",
        "prepayment_percent": "DECIMAL DEFAULT 0",
        "booked": "TEXT DEFAULT ''",
        "booked_time": "INTEGER DEFAULT 0",
        "delivery_code": "INTEGER DEFAULT 0",
        "delivery_user_id": "INTEGER DEFAULT 0",
        "miscellaneous": "TEXT DEFAULT ''"}
    gcode = {
        "id": "INTEGER PRIMARY KEY",
        "order_id": "INTEGER DEFAULT 0",
        "file_id": "TEXT DEFAULT ''",
        "screenshot": "TEXT DEFAULT ''",
        "status": "TEXT DEFAULT ''",
        "duration": "INTEGER DEFAULT 0",
        "weight": "INTEGER DEFAULT 0",
        "booked": "TEXT DEFAULT ''",
        "start_datetime": "DATETIME DEFAULT ''"}
    setting = {
        "id": "INTEGER DEFAULT 0",
        "name": "TEXT PRIMARY KEY",
        "value": "TEXT DEFAULT ''"}
    request = {
        "id": "INTEGER PRIMARY KEY",
        "user_id": "INTEGER DEFAULT 0",
        "created": "DATETIME DEFAULT ''",
        "text": "TEXT DEFAULT ''"}