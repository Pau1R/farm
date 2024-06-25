from lib.order.gcode.Gcode import Gcode
from lib.Msg import Message

class Test:
	app = None

	def __init__(self, app):
		self.app = app
		self.testing()

	def testing(self):
		for chat in self.app.chats:
			if chat.user_id == 7333126996:
				validate = chat.user.designer.validate
				for order in self.app.orders:
					if order.id == 1:
						validate.order = order
						validate.gcode_gui.order = order
						# stl.gcode_gui.

				validate.type = 'sketch'
				validate.status = 'prevalidate'
				validate.show_top_menu()
				
				# validate.message = Message('')
				# validate.message.btn_data = '2'
				
				# validate.process_supports()
				# gcode_ = Gcode(self.app, 0)
				# gcode_.quantity = 1
				# gcode_.duration = 200
				# gcode_.file_id = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'
				# gcode_.screenshot = 'BQACAgIAAxkBAAISVWYpXGhOaUIDeaip_L6DOSXb74fHAAL6SwACJ6RJSWTOzdPWK5hrNAQ'
				# stl.gcodes.append(gcode_)
				# stl.order.logical_status = 'validate'
				# self.app.db.update_order(stl.order)

				# link = chat.user.designer.link
				# link.message = Message('')
				# link.message.btn_data = 'accept'
				# for order in self.app.orders:
				#     if order.id == 12:
				#         link.order = order
				# link.process_validate()