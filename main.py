import asyncio
import tkinter as tk
from datetime import datetime
import requests
from telegram import Bot  # Import the Bot class from the correct module

template = """
-----------------------------------------------
To: {dash_address}
Amount: {amount} DASH ($ {usd_amount} / {amd_amount} AMD)
Time: {date} {time}
DASH rate: {rate} $ (Binance)
Sent by @BitcoinOperatorBot
-----------------------------------------------
Transaction: https://blockchair.com/dash/transaction/{transaction_id}
"""

coin_gecko_url = "https://api.coingecko.com/api/v3/simple/price?ids=dash&vs_currencies=usd"

bot_token = "6263739899:AAFnR3Eey-GS_7UhVDCkIl5yAkfSPmyELRQ"
bot_chat_ids = [740279851, 5689462168, 5999761601, 5622141726, 5800431319, 6003046952]  # List of chat IDs to send the message to

rateamd = 388.0  # Set the value of rateamd here


async def get_rate():
    try:
        response = requests.get(coin_gecko_url)
        data = response.json()
        rate = data.get("dash", {}).get("usd")
        return rate
    except Exception as e:
        print("Error occurred while fetching the rate:", e)
        return None


async def generate_transaction():
    rate = await get_rate()
    if rate is None:
        return

    # Get the current time
    now = datetime.now()
    time = now.strftime('%H:%M:%S')

    # Get the user input for other values
    amount = float(dash_entry.get())
    transaction_id = transaction_id_entry.get()
    dash_address = dash_address_entry.get()  # Get the Dash address

    # Get the current date
    date = now.strftime('%Y-%m-%d')

    # Calculate the amounts
    usd_amount = round(rate * amount, 2)
    amd_amount = round(amount * rate * rateamd)

    # Format and display the output
    output = template.format(dash_address=dash_address, amount=amount, usd_amount=usd_amount, amd_amount=amd_amount,
                             date=date, time=time,
                             rate=rate, transaction_id=transaction_id)
    result_label.config(text=output)

    # Send the message to each chat ID
    bot = Bot(token=bot_token)
    for chat_id in bot_chat_ids:
        await bot.send_message(chat_id=chat_id, text=output)


def run_asyncio_loop():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_transaction())


# Create the main window
window = tk.Tk()
window.title("DASH Transaction Generator")

# Create and position the GUI elements
dash_label = tk.Label(window, text="Enter the amount of DASH:")
dash_label.pack()
dash_entry = tk.Entry(window)
dash_entry.pack()

transaction_id_label = tk.Label(window, text="Enter the transaction ID:")
transaction_id_label.pack()
transaction_id_entry = tk.Entry(window)
transaction_id_entry.pack()

dash_address_label = tk.Label(window, text="Enter the Dash address:")
dash_address_label.pack()
dash_address_entry = tk.Entry(window)
dash_address_entry.pack()

generate_button = tk.Button(window, text="Generate", command=run_asyncio_loop)
generate_button.pack()

result_label = tk.Label(window, text="")
result_label.pack()

# Start the tkinter main loop
window.mainloop()
