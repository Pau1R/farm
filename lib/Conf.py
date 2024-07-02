import configparser
import os

class Conf:

	def __init__(self):
		roles = {
			'owner': 'Владелец',
			'admin': 'Администратор',
			'operator': 'Оператор',
			'designer': 'Дизайнер',
			'issue': 'Выдача'
		}
		
		config = configparser.ConfigParser()
		config.read("config.ini")

		if os.path.exists('bot.dev'):
		    self.bot_token = config['Bot']['bot_dev_token'] # dev
		else:
		    self.bot_token = config['Bot']['bot_prod_token'] # prod
		
		self.api_id = config['Client']['api_id']
		self.api_hash = config['Client']['api_hash']