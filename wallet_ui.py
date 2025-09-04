from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from rpc import get_balance

def generate_wallet_card(address):
    balance = get_balance(address)
    img = Image.new("RGB", (500, 300), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("assets/arial.ttf", 24)

    draw.text((20, 50), f"Wallet Address: {address}", fill="white", font=font)
    draw.text((20, 100), f"Balance: {balance:.2f} PANCA", fill="white", font=font)

    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio
