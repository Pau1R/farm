import asyncio
from telebot import TeleBot, types
from telethon import TelegramClient, events
from threading import Thread
from lib.App import App
from lib.Conf import Conf
from typing import Union

# Initialize configurations and bots
conf = Conf()
bot = TeleBot(conf.bot_token)
app = App(bot, conf)

client = TelegramClient('session_name', conf.api_id, conf.api_hash)

@bot.message_handler(func=lambda msg: True, content_types=['text', 'document', 'photo', 'video'])
@bot.callback_query_handler(func=lambda call: True)
def handle_all_messages(message: Union[types.Message, types.CallbackQuery]):
    app.new_message(message)

@client.on(events.NewMessage)
async def message_handler(event):
    # print(event)
    app.telethon_new_message(event)

def run_telebot():
    bot.infinity_polling()

async def run_telethon():
    await client.start()
    await client.run_until_disconnected()

async def main():
    tasks = [
        asyncio.create_task(run_telethon())
    ]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    telebot_thread = Thread(target=run_telebot)
    telebot_thread.start()

    asyncio.run(main())

    telebot_thread.join()