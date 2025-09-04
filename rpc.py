import json
import os
import random

DATABASE_FILE = "database.json"

def load_db():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "w") as f:
            json.dump({}, f)
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DATABASE_FILE, "w") as f:
        json.dump(db, f, indent=4)

def get_balance(address):
    db = load_db()
    if address not in db:
        db[address] = {"balance": 100.0}  # give some test balance
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
