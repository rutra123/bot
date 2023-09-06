import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telegram import Bot

# Define your Telegram bot token here
TELEGRAM_BOT_TOKEN = '6263739899:AAGiO-6W8WMcs-tHY3NZzEG_AyzLPHPXrhM'

# List of Telegram chat IDs to which you want to send the templates
chat_ids = ['740279851', '6564297273']  # Replace with your actual chat IDs

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



# Custom event handler class
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        print("File 'transaction_values.txt' has been modified. Updating template...")
        updated_template = generate_template_from_file('transaction_values.txt')
        send_telegram_message(updated_template)  # Send the updated template to Telegram

# Main program
file_path = 'transaction_values.txt'

# Create an observer and set the custom event handler
observer = Observer()
observer.schedule(MyHandler(), path='.')
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
