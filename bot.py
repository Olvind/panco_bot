import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from wallet_ui import generate_wallet_card
from referral_system import process_referral, reward_referral
from rpc import generate_wallet, get_balance

logging.basicConfig(level=logging.INFO)

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # Replace with your bot token
DATABASE_FILE = "database.json"

# Load or create database
def load_db():
    try:
        with open(DATABASE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(db):
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)

db = load_db()

def start(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    user = db.get(user_id)

    # If new user, create a wallet
    if not user:
        wallet_info = generate_wallet()
        user = {
            "address": wallet_info["address"],
            "private_key": wallet_info["private_key"],
            "referrals": [],
            "last_claim": None
        }
        db[user_id] = user
        save_db(db)

    referral_code = process_referral(user_id, context.args if context.args else None)
    keyboard = [[InlineKeyboardButton("Wallet Card", callback_data="wallet_card")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"Welcome to Pancono Wallet (Mock)!\nYour referral code: {referral_code}",
        reply_markup=reply_markup
    )

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = str(query.from_user.id)

    if query.data == "wallet_card":
        card = generate_wallet_card(db[user_id]["address"])
        query.message.reply_photo(photo=card)

def main():
    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
