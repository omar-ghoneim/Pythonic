import requests
import re
import hashlib
import base64
from datetime import datetime
from telegram import Update, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    PreCheckoutQueryHandler,
)
from keys import TOKEN, PAYMENT_PROVIDER_TOKEN, SECRET_CODE

base_url = "http://127.0.0.1:5000/"


def generate_signature():
    timestamp = str(datetime.utcnow().timestamp())
    code = hashlib.sha256((timestamp + SECRET_CODE).encode()).digest()
    encoded_code = base64.urlsafe_b64encode(code).decode().rstrip("=")
    return timestamp, encoded_code


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
    timestamp, token = generate_signature()
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
                headers = {"timestamp": timestamp, "token": token}
                r = requests.get(base_url + "short", params=payload, headers=headers)
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


async def subscribe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    timestamp, token = generate_signature()
    headers = {"timestamp": timestamp, "token": token}
    r = requests.get(
        base_url + "check_user", params={"chat_id": chat_id}, headers=headers
    )
    if r.status_code == 200:
        if r.text == "trial":
            title = "Unlimited Subscription"
            description = "Subscribe to shorten unlimited number of links"
            payload = "SuperSecret"
            currency = "USD"
            price = 3
            prices = [LabeledPrice("Unlimited", price * 100)]
            await context.bot.send_invoice(
                chat_id,
                title,
                description,
                payload,
                PAYMENT_PROVIDER_TOKEN,
                currency,
                prices,
                need_name=True,
            )
        else:
            await update.message.reply_text("You are already subscribed", quote=True)
    else:
        await update.message.reply_text("Sorry, something went wrong!", quote=True)


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload != "SuperSecret":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    payload = {
        "user_id": update.message.from_user.id,
        "first_name": update.message.from_user.first_name,
    }
    timestamp, token = generate_signature()
    headers = {"timestamp": timestamp, "token": token}
    r = requests.get(base_url + "sub", params=payload, headers=headers)
    if r.ok:
        await update.message.reply_text("Thank you for your payment")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # command handlers
    help_handler = CommandHandler("help", help_callback)
    start_handler = CommandHandler("start", start_callback)
    sub_handler = CommandHandler("subscribe", subscribe_callback)
    precheckout_handler = PreCheckoutQueryHandler(precheckout_callback)
    msg_handler = MessageHandler(filters.TEXT, shorten_link)
    success_payment_handler = MessageHandler(
        filters.SUCCESSFUL_PAYMENT, successful_payment_callback
    )

    # register commands
    app.add_handler(help_handler)
    app.add_handler(start_handler)
    app.add_handler(sub_handler)
    app.add_handler(precheckout_handler)
    app.add_handler(msg_handler)
    app.add_handler(success_payment_handler)
    app.run_polling()
