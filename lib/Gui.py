import time
from telebot import types as tbot
from lib.Msg import Message

class Gui:
	messages = []
	app = None
	chat = None
	address = ''

	def __init__(self, app, chat, address):
		self.app = app
		self.chat = chat
		self.address = address

	def clear_chat(self):
		self.remove_messages(self.messages)

	def clear_order_chat(self, order_id):
		messages = self.chat.user.GUI.messages
		messages.extend(self.messages)
		for message in messages:
			if message.instance_id == str(order_id):
				self.remove_message(message)

	def remove_messages(self, messages):
		for message in messages.copy():
			if message.data == '':
				if message.general_clear:
					self.remove_message(message)
			else:
				if message.general_clear:
					self.list_remove_message(message)

	def remove_message(self, message):
		try:
			self.app.bot.delete_message(message.chat_id, message.id)
			print('bot remove message', message.chat_id, message.id)
			self.list_remove_message(message)
		except Exception as e:
			self.list_remove_message(message)
			print ('delete error:', message.chat_id, message.id, e)

	def messages_append(self, message):
		self.messages = self.messages + [message]

	def list_remove_message(self, message):
		try:
			self.messages.remove(message)
		except:
			x = ''
		try:
			self.chat.user.GUI.messages.remove(message)
		except:
			x = ''

	def tell(self, text):
		self.messages_append(Message(self.app.bot.send_message(self.chat.user_id, text)))

	def tell_permanent(self, text):
		message = Message(self.app.bot.send_message(self.chat.user_id, text))
		return message

	def tell_id(self, id, text):
		Message(self.app.bot.send_message(id, text))

	def tell_document_buttons(self, document, caption, bts, strict_, function_id, object_id):
		buttons = self.buttons_address(bts, function_id, object_id)
		strict = self.buttons_address(strict_, function_id, object_id)
		buttons = self.prepare_buttons(buttons, strict)
		message = Message(self.app.bot.send_document(self.chat.user_id, document=document, caption=caption, reply_markup=buttons))
		self.messages_append(message)

	def tell_document(self, document, caption):
		message = Message(self.app.bot.send_document(self.chat.user_id, document=document, caption=caption))
		self.messages_append(message)

	def tell_photo(self, caption, photo):
		if photo == '':
			self.tell(caption)
		message = Message(self.app.bot.send_photo(self.chat.user_id, photo=photo, caption=caption))
		self.messages_append(message)
		return message

	def tell_photo_buttons(self, caption, photo, bts, strict_, function_id, object_id):
		if photo == '':
			self.tell_buttons(caption, bts, strict)
		buttons = self.buttons_address(bts, function_id, object_id)
		strict = self.buttons_address(strict_, function_id, object_id)
		buttons = self.prepare_buttons(buttons, strict)
		message = Message(self.app.bot.send_photo(self.chat.user_id, photo=photo, caption=caption, reply_markup=buttons))
		self.messages_append(message)
		return message

	def tell_buttons(self, text, bts, strict_, function_id, object_id):
		buttons = self.buttons_address(bts, function_id, object_id)
		strict = self.buttons_address(strict_, function_id, object_id)
		buttons = self.prepare_buttons(buttons, strict)
		message = Message(self.app.bot.send_message(self.chat.user_id, text, reply_markup=buttons))
		self.messages_append(message)
		return message

	def tell_buttons_id(self, id, text, bts, strict_, function_id, object_id):
		buttons = self.buttons_address(bts, function_id, object_id)
		strict = self.buttons_address(strict_, function_id, object_id)
		buttons = self.prepare_buttons(buttons, strict)
		message = Message(self.app.bot.send_message(id, text, reply_markup=buttons))
		self.messages_append(message)
		return message

	def buttons_address(self, buttons_, function_id, object_id):
		new_buttons = []
		buttons = buttons_.copy()
		for button in buttons:
			btn = ['','']
			btn[1] = '~' + self.address + '|' + str(function_id) + '|' + str(object_id) + '|'
			if type(button) is list:
				btn[0] = button[0]
				if len(button) > 1:
					btn[1] = btn[1] + str(button[1])
				else:
					btn[1] = btn[1] + button[0]
			else:
				btn[0] = button
				btn[1] = btn[1] + button
			new_buttons.append(btn)
		return new_buttons

	def prepare_buttons(self, bts_, strict_):
		buttons = tbot.InlineKeyboardMarkup()
		max_row_text_length = 30
		bts = bts_.copy()
		strict = strict_.copy()
		while len(bts) > 0:
			new_row = []
			row_text_length = 0
			max_row_buttons = 6
			elem = 0
			while True:
				elem += 1
				if elem > max_row_buttons:
					break
				button = bts[0]     # get first element of bts

				# get text and data from button
				button_data = ''
				if type(button) is list:
					button_text = button[0]
					if len(button) > 1:
						button_data = str(button[1])
				else:
					button_text = button
				# count button text length
				button_length = len(str(button_text))

				# if at least one button is greater than the limit for each coloumn size then lower coloumn amount
				if max_row_buttons == 6 and button_length > 4:
					max_row_buttons -= 1
				if max_row_buttons == 5 and button_length > 6:
					max_row_buttons -= 1
				if max_row_buttons == 4 and button_length > 9:
					max_row_buttons -= 1
				if max_row_buttons == 3 and button_length > 12:
					max_row_buttons -= 1
				if max_row_buttons == 2 and button_length > 15:
					max_row_buttons -= 1

				# stop appending to row if row text length is greater than the overall row limit
				row_text_length += button_length
				if elem != 1:
					if row_text_length > max_row_text_length:
						break

				# if button is an interface key then display only it on a row
				flag = False
				for entry in strict:
					txt = entry
					data = ''
					if type(entry) is list:
						txt = entry[0]
						if len(entry) > 1:
							data = str(entry[1])
					# if button_text == txt:
					if button_text == txt and button_data == data:
						if elem == 1:
							new_row.append(button)
							del bts[0]
							flag = True
						else:
							flag = True
				if not flag:
					new_row.append(button)
					del bts[0]

				if flag:
					break

				# if button is an interface key then display only it on a row
				# if button_text in strict:
				# 	if elem == 1:
				# 		new_row.append(button)
				# 		del bts[0]
				# 		break
				# 	else:
				# 		break
				# else:
				# 	new_row.append(button)
				# 	del bts[0]

				# if there is no more buttons then stop adding buttons to row
				if len(bts) == 0:
					break
			# account for difference in callback_data
			row = []
			for button in new_row:
				if type(button) is list and len(button) > 1:
					row.append(tbot.InlineKeyboardButton(button[0], callback_data=button[1]))
				else:
					if type(button) is list:
						button = ''.join(button)
					row.append(tbot.InlineKeyboardButton(button, callback_data=button))

			# construct telebot rows
			if len(row) == 1:
				buttons.row(row[0])
			elif len(row) == 2:
				buttons.row(row[0], row[1])
			elif len(row) == 3:
				buttons.row(row[0], row[1], row[2])
			elif len(row) == 4:
				buttons.row(row[0], row[1], row[2], row[3])
			elif len(row) == 5:
				buttons.row(row[0], row[1], row[2], row[3], row[4])
			elif len(row) == 6:
				buttons.row(row[0], row[1], row[2], row[3], row[4], row[5])
		# self.messages.append(Message(self.app.bot.send_message(self.chat.user_id, text, reply_markup=buttons)))
		return buttons