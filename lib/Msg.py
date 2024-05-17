class Message:
	chat_id = ''
	user_id = ''
	user_name = ''
	id = ''
	type = ''
	text = ''
	caption = ''
	file_id = ''
	file_name = ''
	data = ''
	order_id = ''
	general_clear = True

	data_special_format = False
	file1 = ''
	file2 = ''
	file3 = ''
	file4 = ''
	function = ''
	btn_user_id = ''
	instance_id = ''
	btn_data = ''

	def __init__(self, message):
		# print('------------')
		# print(message)
		# print('------------')
		# self.user_id = message.from_user.id
		# self.chat_id = message.chat.id

		try:
			self.chat_id = str(message.json['chat']['id'])
		except:
			self.chat_id = str(message.json['message']['chat']['id'])
		self.user_id = str(message.json['from']['id'])

		self.user_name = str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)
		if len(self.user_name) < 2:
			self.user_name = message.from_user.user_name
		if self.user_name == '':
			self.user_name = message.from_user.id
		
		try:
			self.id = str(message.message.id)
		except:
			self.id = str(message.message_id)

		if hasattr(message, 'data'):
			self.type = 'button'
			self.data = message.data
			self.data_to_special_format(message.data)
		else:
			if hasattr(message, 'content_type'):
				if message.content_type == 'document':
					self.type = 'document'
					self.file_id = str(message.json['document']['file_id'])
					self.file_name = str(message.json['document']['file_name'])
				elif message.content_type == 'photo':
					self.type = 'photo'
					self.file_id = str(message.json['photo'][3]['file_id'])
				elif message.content_type == 'video':
					self.type = 'video'
					self.file_id = str(message.video.file_id)
				else:
					self.type = 'text'
					if message.text != None:
						self.text = message.text.strip()

		# print(self.file_id)

		if hasattr(message, 'caption'):
			if message.caption != None:
				self.caption = message.caption.strip()

	def data_to_special_format(self, data):
		self.data_special_format = True
		address = data.split('|')[0]
		address = address.split("~")[1]
		# if address.count('/') >= 0:
		self.file1 = address.split('/')[0]
		if address.count('/') > 0:
			self.file2 = address.split('/')[1]
		if address.count('/') > 1:
			self.file3 = address.split('/')[2]
		if address.count('/') > 2:
			self.file4 = address.split('/')[3]
		if data.count('|') > 0:
			self.function = data.split('|')[1]
		if data.count('|') > 1:
			self.instance_id = data.split('|')[2]
		if data.count('|') > 2:
			self.btn_data = data.split('|')[3]

# BUTTON DATA SPECIAL FORMAT SPECIFICATIONS:
# Special chars:
# ~ - data field is in special format
# | - global delimeter
# / - file(class) path delimeter

# data field parts:
#   1 - path
#   2 - function id
#   3 - instance_id
#   4 - button data

# examples:
# ~4/1/3|2|instance_id|yes





		# getting button presses

		# print('creating Message. user_id:', self.user_id, 
		# 	  'chat.id:', self.chat_id, 
		# 	  'id:', self.id, 
		# 	  'text:', self.text, 
		# 	  'data:', self.data, 
		# 	  'user_name:', self.user_name)