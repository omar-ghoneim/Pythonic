import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from keys import TOKEN

base_url = "http://127.0.0.1:5000/"


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hi, I am a link shortening bot. To start click on /start",
    )


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="To shorten a link, please send the link",
    )


async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    r = requests.get(base_url, params={"text": message_text})
    await context.bot.send_message(chat_id=update.effective_chat.id, text=r.text)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # command handlers
    help_handler = CommandHandler("help", help_callback)
    start_handler = CommandHandler("start", start_callback)
    msg_handler = MessageHandler(filters.TEXT, msg)
    # register commands
    app.add_handler(help_handler)
    app.add_handler(start_handler)
    app.add_handler(msg_handler)
    app.run_polling()
