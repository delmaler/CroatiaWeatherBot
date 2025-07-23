from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,MessageHandler, filters
from dotenv import load_dotenv
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from fetch import fetch_weather_report
load_dotenv()
bot_token = os.getenv('TELEGRAM_TOKEN')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        report = fetch_weather_report()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Weather report fetched successfully!")
        # Send the title
        await context.bot.send_message(chat_id=update.effective_chat.id, text=report['title'])
        # Send each section
        for section in report['report']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"**{section['section']}**\n{section['content']}")
    except Exception as e:
        logging.error(f"Error fetching weather report: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to fetch weather report.")
        
async def other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Try using the /Weather command.")
    
if __name__ == '__main__':
    application = ApplicationBuilder().token(bot_token).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    weather_handler = CommandHandler('weather', weather)
    application.add_handler(weather_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, other))

    application.run_polling()
