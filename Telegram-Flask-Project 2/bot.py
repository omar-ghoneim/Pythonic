import requests
import re
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


async def shorten_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    chat_id = update.message.from_user.id

    try:
        pattern = re.compile(
            r"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)"
        )
        matches = re.findall(pattern, message_text)
        if matches:
            for link in matches:
                payload = {
                    "link": link,
                    "username": username,
                    "first_name": first_name,
                    "chat_id": chat_id,
                }

                r = requests.get(base_url + "short", params=payload)
                if r.status_code == 200:
                    result = r.json()
                    if result.get("status") == "success":
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"Here is your short link: {result.get('shortened_link')}",
                        )
                    else:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text="Sorry you have exhausted all of your free trials. Please /subscribe to continue using our service",
                        )
                else:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="Sorry, something went wrong!",
                    )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text=f"The message does not contain a link"
            )
    except:
        await context.bot.send_message(
            chat_id=chat_id, text="Sorry, could not parse the link"
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # command handlers
    help_handler = CommandHandler("help", help_callback)
    start_handler = CommandHandler("start", start_callback)
    msg_handler = MessageHandler(filters.TEXT, shorten_link)
    # register commands
    app.add_handler(help_handler)
    app.add_handler(start_handler)
    app.add_handler(msg_handler)
    app.run_polling()
