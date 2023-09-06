import httpx
from datetime import datetime
from telegram import Bot
import pytz
import trio
import warnings
import hashlib

warnings.filterwarnings("ignore", category=RuntimeWarning, module="trio")

# Set the timezone to Armenia Standard Time
armenia_timezone = pytz.timezone('Asia/Yerevan')

# Function to read transaction values from the file
def read_transaction_values(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        print("Error: 'transaction_values.txt' file not found.")
        exit()

# Function to convert a value to a safe float
def safe_float(value):
    try:
        return float(value.strip()) if value.strip() else None
    except ValueError:
        return None

# Function to format a USD amount
def format_usd_amount(amount):
    if amount.is_integer():
        return f"${int(amount)}"
    return f"${amount:.1f}".rstrip('0').rstrip('.')

# Function to process transaction data from the file
def process_transaction_data(lines):
    dash_address = lines[0].strip()
    amount = safe_float(lines[3])
    rate = safe_float(lines[8])

    if None in (amount, rate):
        print("Error: 'amount' or 'rate' is not a valid float in the file.")
        exit()

    usd_amount = amount * rate
    amd_amount = 392 * amount * rate
    date_time = lines[2].strip()
    transaction_id = lines[1].strip()

    return dash_address, amount, usd_amount, amd_amount, date_time, rate, transaction_id

# Function to generate a transaction template
def generate_transaction_template(data):
    dash_address, amount, usd_amount, amd_amount, date_time, rate, transaction_id = data

    template = """
    -----------------------------------------------
    To: {dash_address}
    Amount: {amount} DASH ({usd_amount} / {amd_amount:.0f} AMD) 
    Time: {date_time}
    DASH rate: ${rate:.2f} (binance)
    Sent by @BitcoinOperator
    -----------------------------------------------
    Transaction: https://blockchair.com/dash/transaction/{transaction_id}"""

    return template.format(
        dash_address=dash_address,
        amount=amount,
        usd_amount=format_usd_amount(usd_amount),
        amd_amount=amd_amount,
        date_time=date_time,
        rate=rate,
        transaction_id=transaction_id
    )

            # Format and display the output
            output = template.format(dash_address=dash_address, amount=amount, usd_amount=usd_amount, amd_amount=amd_amount,
                                     date=date_time.strftime('%Y-%m-%d'), time=date_time.strftime('%H:%M:%S'),
                                     rate=rate, transaction_id=transaction_id)
            print(output)

            # Send the message to each chat ID
            bot = Bot(token=bot_token)
            for chat_id in bot_chat_ids:
                await bot.send_message(chat_id=chat_id, text=output)  # Await the send_message call

    except Exception as e:
        print("Error occurred during transaction generation:", e)

def run_trio_loop():
    while True:
        trio.run(generate_transaction)

if __name__ == "__main__":
    run_trio_loop()
