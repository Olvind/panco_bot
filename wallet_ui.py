import json
import os
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

DATABASE_FILE = "database.json"

# ------------------ Mock DB Functions ------------------

def load_db():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "w") as f:
            json.dump({}, f)
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)

# ------------------ Mock Blockchain Functions ------------------

def get_balance(address):
    db = load_db()
    if address not in db:
        db[address] = {"balance": 100.0}  # test starting balance
        save_db(db)
    return db[address]["balance"]

def send_transaction(from_addr, to_addr, amount, private_key=None):
    db = load_db()
    db.setdefault(from_addr, {"balance": 100.0})
    db.setdefault(to_addr, {"balance": 0.0})
    
    if db[from_addr]["balance"] < amount:
        return "Insufficient balance"
    
    db[from_addr]["balance"] -= amount
    db[to_addr]["balance"] += amount
    save_db(db)
    
    return f"tx_{random.randint(100000,999999)}"

def generate_wallet():
    address = f"0x{random.randint(10**15,10**16-1)}"
    private_key = f"priv_{random.randint(100000,999999)}"
    return {"address": address, "private_key": private_key}

# ------------------ Wallet Card UI Functions ------------------

def generate_wallet_card(address):
    balance = get_balance(address)
    
    img = Image.new("RGB", (500, 300), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    
    # Load font, fallback to default if missing
    font_path = "assets/arial.ttf"
    if os.path.exists(font_path):
        font = ImageFont.truetype(font_path, 24)
    else:
        font = ImageFont.load_default()
    
    draw.text((20, 50), f"Wallet Address: {address}", fill="white", font=font)
    draw.text((20, 100), f"Balance: {balance:.2f} PANCA", fill="white", font=font)
    
    # Optional: add logo if available
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).resize((80, 80))
            img.paste(logo, (400, 200), logo.convert("RGBA"))
        except Exception as e:
            print(f"Logo could not be added: {e}")
    
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio
