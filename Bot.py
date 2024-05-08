import sys
# sys.path.insert(0,'lib/')
from lib.App import App
from lib.Conf import Conf
import telebot

conf = Conf()

bot = telebot.TeleBot(conf.bot_token)

# all messages receiver (also underinput button handler)
@bot.message_handler(func=lambda MSG: True)
def messageReceiver(message):
    app.new_message(message)

# inline button presses
@bot.callback_query_handler(func=lambda call: True)
def callback(message):
    app.new_message(message)

# inline button presses
@bot.message_handler(content_types=['document', 'photo', 'video']) # ['document', 'photo', 'audio', 'video', 'voice']
def fileReceiver(message):
    # print('message received ')
    # print(message)
    # file_name = message.document.file_name
    # file_info = bot.get_file(message.document.file_id)
    # print(file_name, file_info)
    # downloaded_file = bot.download_file(file_info.file_path)
    # with open(file_name, 'wb') as new_file:
    #     new_file.write(downloaded_file)
    app.new_message(message)

app = App(bot, conf)

bot.infinity_polling()