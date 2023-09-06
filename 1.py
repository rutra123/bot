import requests
import time
import datetime

# Replace with your Dash address
address = "XeDXWLwGMQGPyVXnuk1DG3T2pX6p7yabNx"

# Initialize the last processed transaction ID as None
last_txid = None

# Define the filename for the text file
file_name = "transaction_values.txt"

# Define the Binance API URL to get the USDT rate
binance_api_url = "https://api.binance.com/api/v3/ticker/price?symbol=DASHUSDT"

# Define the interval for checking new transactions (in seconds)
check_interval = 2  # Check every 2 seconds

def fetch_utxos(address):
    api_url = f"https://insight.dash.org/insight-api/addr/{address}/utxo"
    response = requests.get(api_url)
    return response

def fetch_transaction(txid):
    api_url = f"https://insight.dash.org/insight-api/tx/{txid}"
    response = requests.get(api_url)
    return response

def process_utxo(utxo):
    new_txid = utxo["txid"]
    return new_txid

def fetch_and_process_transaction(address, last_txid, file_name, check_interval):
    try:
        response = fetch_utxos(address)
        if response.status_code == 200:
            utxos = response.json()
            if len(utxos) > 0:
                latest_utxo = utxos[0]
                new_txid = process_utxo(latest_utxo)
                if new_txid != last_txid:
                    received_value = latest_utxo["satoshis"] / 1e8

                    transaction_response = fetch_transaction(new_txid)
                    if transaction_response.status_code == 200:
                        transaction_data = transaction_response.json()
                        sender_address = transaction_data["vin"][0]["addr"]

                        binance_response = requests.get(binance_api_url)
                        if binance_response.status_code == 200:
                            binance_data = binance_response.json()
                            rate_str = binance_data.get("price")
                        else:
                            print("Failed to retrieve Binance rate.")
                            print(f"Status Code: {binance_response.status_code}")
                            print(f"Response Content: {binance_response.text}")
                            rate_str = "N/A"

                        total_inputs = sum(float(input_tx["value"]) for input_tx in transaction_data["vin"])
                        total_outputs = sum(float(output_tx["value"]) for output_tx in transaction_data["vout"])
                        fee = (total_inputs - total_outputs)

                        print_transaction_info(
                            address, new_txid, received_value, sender_address, fee, total_inputs, total_outputs, rate_str)

                        write_transaction_info_to_file(
                            file_name, address, new_txid, received_value, sender_address, fee, total_inputs,
                            total_outputs, binance_api_url, rate_str)
                        return new_txid  # Return the new_txid value
                    else:
                        print("Failed to retrieve transaction details.")
                else:
                    print("Waiting...")
            else:
                print("Waiting for transactions...")
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
        time.sleep(check_interval)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    return last_txid  # Return the last_txid value if an exception occurs

def print_transaction_info(address, new_txid, received_value, sender_address, fee, total_inputs, total_outputs, rate_str):
    print(f"Dash Address: {address}")
    print(f"Transaction ID: {new_txid}")
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Appearing Time (Current System Time): {current_time}")
    print(f"Received Value: {received_value:.8f} DASH")
    print(f"Sender Address: {sender_address}")
    print(f"Transaction Fee: {fee:.8f} DASH")
    print(f"Total Inputs: {total_inputs:.8f}")
    print(f"Total Outputs: {total_outputs:.8f}")
    print(f"Binance USDT Rate: {rate_str}")

def write_transaction_info_to_file(file_name, address, new_txid, received_value, sender_address, fee, total_inputs, total_outputs, binance_api_url, rate_str):
    with open(file_name, "w") as file:  # Use "w" mode to overwrite the file
        file.write(f"{address}\n")
        file.write(f"{new_txid}\n")
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(f"{current_time}\n")
        file.write(f"{received_value:.8f}\n")
        file.write(f"{sender_address}\n")
        file.write(f"{fee:.8f}\n")
        file.write(f"{total_inputs:.8f}\n")
        file.write(f"{total_outputs:.8f}\n")
        file.write(f"{rate_str}\n\n")

def main():
    global last_txid
    while True:
        last_txid = fetch_and_process_transaction(address, last_txid, file_name, check_interval)

if __name__ == "__main__":
    main()
