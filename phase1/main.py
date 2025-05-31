from collections import deque
from time import sleep
from datetime import datetime

import requests

endpoint = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_last_updated_at=true"


def get_bitcoin_price(session: requests.Session) -> tuple:
    response = session.get(endpoint)
    response.raise_for_status()
    data = response.json()
    return data['bitcoin']['usd'], data['bitcoin']['last_updated_at']


def count_avarage(storage: deque) -> float:
    if not storage:
        return 0.0
    return sum(storage) / len(storage)


def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    })
    storage = deque(maxlen=10)
    sleeptime = 1
    fetching_failures = 0
    try:
        while True:
            sleep(sleeptime)
            try:
                price, last_updated = get_bitcoin_price(session)
            except requests.RequestException as e:
                sleeptime *= 2
                fetching_failures += 1
                if fetching_failures >= 5:
                    print(f"Error occurred while fetching data: {e}")
                    fetching_failures = 0
                continue
            if price is not None:
                sleeptime = 1
                storage.append(price)
                average_price = count_avarage(storage)
                last_updated_dt = datetime.fromtimestamp(last_updated).strftime('%Y-%m-%dT%H:%M:%S')
                print(f"[{last_updated_dt}] BTC → USD: ${price} | SMA({len(storage)}): ${average_price:.2f}")
            else:
                print("Failed to retrieve Bitcoin price.")
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        session.close()


if __name__ == "__main__":
    main()
