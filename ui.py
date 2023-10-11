from telebot.async_telebot import AsyncTeleBot
import asyncio
import os

from main_console import get_llm_response
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage


bot = AsyncTeleBot(os.environ['TELEGRAM_API_TOKEN'])

messages = []

llm = ChatOpenAI(model='gpt-4-0613')
thought_llm = ChatOpenAI(model='gpt-4-0613')

# Handle '/start'
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
ChatBot started.
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def respond(message):
    messages.append(HumanMessage(content=message.text))
    response = get_llm_response(messages, llm, thought_llm)
    await bot.reply_to(message, response)


def main():
    asyncio.run(bot.polling())



if __name__ == '__main__':
    main()