import trio
import httpx
from datetime import datetime
from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters  # Добавьте эти импорты
import sys
import asyncio

async def my_coroutine():
    # Do some work here...
    await asyncio.sleep(1)

# Восстановить предыдущий обработчик sys.excepthook
sys.excepthook = sys.__excepthook__

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

# States for the conversation
WAITING_AMOUNT, WAITING_TRANSACTION_ID, WAITING_DASH_ADDRESS = range(3)

# Chat IDs
with open("chat_ids.txt", "r") as file:
    bot_chat_ids = [int(line.strip()) for line in file if line.strip()]

coin_gecko_url = "https://api.coingecko.com/api/v3/simple/price?ids=dash&vs_currencies=usd"
bot_token = "6263739899:AAH0lAXOJC1r_Azek2wVGOFqPApuZXg9hls"  # Replace with your actual bot token
rateamd = 388.0

async def get_rate():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(coin_gecko_url)
            data = response.json()
            rate = data.get("dash", {}).get("usd")
            return rate
    except Exception as e:
        print("Error occurred while fetching the rate:", e)
        return None

async def generate_transaction(update, context):
    rate = await get_rate()
    if rate is None:
        update.message.reply_text("Error fetching DASH rate. Please try again later.")
        return

    now = datetime.now()
    time = now.strftime('%H:%M:%S')

    user_data = context.user_data
    amount = user_data.get("amount")
    transaction_id = user_data.get("transaction_id")
    dash_address = user_data.get("dash_address")

    date = now.strftime('%Y-%m-%d')

    amount = float(amount)
    usd_amount = round(rate * amount, 2)
    amd_amount = round(amount * rate * rateamd)

    output = template.format(dash_address=dash_address, amount=amount, usd_amount=usd_amount, amd_amount=amd_amount,
                             date=date, time=time,
                             rate=rate, transaction_id=transaction_id)

    bot = context.bot
    for chat_id in bot_chat_ids:
        await bot.send_message(chat_id=chat_id, text=output)

    update.message.reply_text("Transaction created and sent!")

    # Clear user data after the transaction
    user_data.clear()
    return ConversationHandler.END

def start(update, context):
    user_id = update.message.from_user.id
    context.user_data[user_id] = {"step": WAITING_AMOUNT}  # Инициализация ключа "step"
    update.message.reply_text("Введите сумму DASH:")
    return WAITING_AMOUNT

def cancel(update, context):
    user_data = context.user_data
    user_data.clear()
    update.message.reply_text("Создание транзакции отменено.")
    return ConversationHandler.END

def handle_user_input(update, context):
    user_id = update.message.from_user.id
    user_data = context.user_data
    text = update.message.text

    if "step" not in user_data[user_id]:
        update.message.reply_text("Чтобы начать, отправьте команду /start.")
        return

    if user_data[user_id]["step"] == WAITING_AMOUNT:
        user_data[user_id]["amount"] = text
        update.message.reply_text("Введите ID транзакции DASH:")
        user_data[user_id]["step"] = WAITING_TRANSACTION_ID
    elif user_data[user_id]["step"] == WAITING_TRANSACTION_ID:
        user_data[user_id]["transaction_id"] = text
        update.message.reply_text("Введите адрес DASH:")
        user_data[user_id]["step"] = WAITING_DASH_ADDRESS
    elif user_data[user_id]["step"] == WAITING_DASH_ADDRESS:
        user_data[user_id]["dash_address"] = text
        # Call the transaction generation function
        trio.run(generate_transaction, update, context)
    return WAITING_AMOUNT

def main():
    updater = Updater(token=bot_token, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, handle_user_input)],
            WAITING_TRANSACTION_ID: [MessageHandler(Filters.text & ~Filters.command, handle_user_input)],
            WAITING_DASH_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, handle_user_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
