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

# TeleBot handlers
@bot.message_handler(func=lambda msg: True)
@bot.callback_query_handler(func=lambda call: True)
def handle_all_messages(message: Union[types.Message, types.CallbackQuery]):
    app.new_message(message)

# Telethon handler
@client.on(events.NewMessage)
async def message_handler(event):
    app.telethon_new_message(event.message.message)

# Function to run TeleBot polling
def run_telebot():
    bot.infinity_polling()

# Asynchronous function to start and run Telethon client
async def run_telethon():
    await client.start()
    await client.run_until_disconnected()

# Main function to run both bots concurrently
async def main():
    tasks = [
        asyncio.create_task(run_telethon())
    ]
    await asyncio.gather(*tasks)

# Run the main function and TeleBot in separate threads
if __name__ == '__main__':
    telebot_thread = Thread(target=run_telebot)
    telebot_thread.start()

    asyncio.run(main())

    telebot_thread.join()