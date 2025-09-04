from dotenv import load_dotenv
import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from wallet_ui import generate_wallet_card
from referral_system import process_referral, reward_referral
from rpc import generate_wallet, get_balance, send_transaction

# Load environment variables from .env
load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = os.environ.get("ADMIN_IDS", "")
ADMIN_IDS = [int(uid) for uid in ADMIN_IDS.split(",") if uid]

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in the .env file!")

logging.basicConfig(level=logging.INFO)

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

# /start command
def start(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    user = db.get(user_id)

    # Create wallet if new
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

    keyboard = [
        [InlineKeyboardButton("Wallet Card", callback_data="wallet_card")],
        [InlineKeyboardButton("My Referrals", callback_data="my_referrals")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"Welcome to Pancono Wallet (Mock)!\nYour referral code: {referral_code}",
        reply_markup=reply_markup
    )

# /admin command
def admin(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("You are not authorized to access admin panel.")
        return

    keyboard = [[InlineKeyboardButton("View Users & Referrals", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Admin Panel", reply_markup=reply_markup)

# Inline button handler
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = str(query.from_user.id)

    if query.data == "wallet_card":
        card = generate_wallet_card(db[user_id]["address"])
        query.message.reply_photo(photo=card)

    elif query.data == "my_referrals":
        user = db[user_id]
        referral_count = len(user.get("referrals", []))
        query.message.reply_text(
            f"You have referred {referral_count} user(s).\n"
            f"Referral list: {', '.join(user.get('referrals', [])) if referral_count>0 else 'None'}"
        )

    elif query.data == "admin_panel" and int(user_id) in ADMIN_IDS:
        lines = [f"Total Users: {len(db)}\n"]
        for uid, info in db.items():
            lines.append(f"User {uid}: {len(info.get('referrals', []))} referrals")
        query.message.reply_text("\n".join(lines))

# Main bot function
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
