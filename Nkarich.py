from PIL import Image, ImageDraw, ImageFont
from telegram import Bot
import asyncio
from datetime import datetime, timedelta
import requests
import os.path
import time


# Define a function to add text to an image
def add_text_to_image(image, text, coordinates, font_path, font_size, font_color):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(coordinates, text, font=font, fill=font_color)


# Define a function to get the DASH amount in USD using the CoinGecko API
def get_usd_amount_online(dash_amount):
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=dash&vs_currencies=usd')
        response.raise_for_status()
        data = response.json()
        dash_usd_price = data.get('dash', {}).get('usd')
        if dash_usd_price is not None:
            return dash_amount * dash_usd_price
        else:
            raise Exception("Failed to fetch DASH price in USD from the API")
    except requests.exceptions.RequestException as e:
        raise Exception("Network request error:", e)
    except Exception as e:
        raise Exception("API data processing error:", e)


# Open the image
img = Image.open('QART2.jpg')

# Define font settings
font_path = 'arial.ttf'
font_size = 30
font_color = (19, 18, 23)

# Create drawing objects for the image
draw = ImageDraw.Draw(img)

# Initialize the Telegram bot with your token
bot_token = "6263739899:AAGiO-6W8WMcs-tHY3NZzEG_AyzLPHPXrhM"
bot = Bot(token=bot_token)


# Define a function to send the image to Telegram users
async def send_image_to_users(chat_ids):
    try:
        for chat_id in chat_ids:
            with open("car2.png", "rb") as image_file:
                await bot.send_photo(chat_id=chat_id, photo=image_file)
                print("Image sent via Telegram to chat ID:", chat_id)
    except Exception as e:
        print("Error sending the image:", e)


# Function to check for changes in the file
def check_file_changes(file_path):
    last_modified = os.path.getmtime(file_path)
    while True:
        time.sleep(5)  # Check for changes every 5 seconds (you can adjust the interval)
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:
            last_modified = current_modified
            with open("transaction_values.txt", "r") as file:
                lines = file.read().splitlines()

            # Process and update the image with new data
            date_time_str = lines[2]
            month_names = [
                "января", "февраля", "марта", "апреля", "мая", "июня",
                "июля", "августа", "сентября", "октября", "ноября", "декабря"
            ]
            formatted_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
            formatted_datetime = formatted_datetime.replace(month=(formatted_datetime.month + 0) % 12)
            adjusted_end_time = formatted_datetime - timedelta(minutes=2)
            formatted_adjusted_end_time = adjusted_end_time.strftime("%-d {} %I:%M").format(
                month_names[adjusted_end_time.month - 1])

            # ... (continue with the rest of your code to update the image)

            # Save the updated image
            img.save("car2.png")


# Start the file change monitoring loop in the background
file_path = "transaction_values.txt"
file_change_task = asyncio.create_task(check_file_changes(file_path))

# Event loop for Telegram bot functionality
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        # Your code to get chat_ids
        chat_ids = [740279851]  # Replace with your actual chat_ids
        if chat_ids:
            loop.run_until_complete(send_image_to_users(chat_ids))
        else:
            print("No available or valid chat_ids.")
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C to exit gracefully
    finally:
        loop.run_until_complete(file_change_task)  # Wait for the file change monitoring task
        loop.close()
