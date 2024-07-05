from lib.order.gcode.Gcode import Gcode
from lib.Msg import Message

class Test:
	app = None

	def __init__(self, app):
		self.app = app
		self.testing()

	def testing(self):
		for chat in self.app.chats:
			if chat.user_id == 7246224587:
				for order in self.app.orders:
					if order.id == 2:
						chat.user.admin.order_GUI.edit.order = order
						chat.user.admin.order_GUI.edit.show_top_menu()

				# general.printer_type = 'Creality ender 3 s1 pro'
				# general.plastic_type = 'PETG'
				# general.weight = 4
				# general.support_time = 0

				# general.gcode_gui.gcode = Gcode(self.app, 0)
				# general.gcode_gui.show_top_menu()
				
				# general.message = Message('')
				# general.message.btn_data = '2'
				
				# general.process_supports()
				# gcode_ = Gcode(self.app, 0)
				# gcode_.quantity = 1
				# gcode_.duration = 200
				# gcode_.file_id = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'
				# gcode_.screenshot = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'
				# stl.gcodes.append(gcode_)
				# stl.order.logical_status = 'general'
				# self.app.db.update_order(stl.order)

				# link = chat.user.designer.link
				# link.message = Message('')
				# link.message.btn_data = 'accept'
				# for order in self.app.orders:
				#     if order.id == 12:
				#         link.order = order
				# link.process_general()