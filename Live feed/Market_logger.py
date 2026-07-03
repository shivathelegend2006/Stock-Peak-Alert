#Om Namo Venketesaya

import csv
import time
from datetime import datetime
import requests



# -----------------------------
# Create session
# -----------------------------
session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Visit homepage once
session.get(
    "https://www.nseindia.com",
    headers=headers
)


# -----------------------------
# CSV filename
# -----------------------------
today = datetime.now().strftime("%Y-%m-%d")

filename = f"market_{today}.csv"


# -----------------------------
# Create CSV
# -----------------------------
with open(filename, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Timestamp",
        "Price",
        "Open",
        "High",
        "Low",
        "Previous Close",
        "Percent Change"
    ])

    print(f"\nLogging to {filename}\n")

    while True:

        try:

            response = session.get(
                "https://www.nseindia.com/api/allIndices",
                headers=headers,
                timeout=5
            )

            data = response.json()

            for item in data["data"]:

                if item["index"] == "NIFTY 50":

                    timestamp = datetime.now()

                    price = item["last"]

                    open_price = item["open"]

                    high = item["high"]

                    low = item["low"]

                    previous_close = item["previousClose"]

                    percent_change = item["percentChange"]

                    writer.writerow([
                        timestamp,
                        price,
                        open_price,
                        high,
                        low,
                        previous_close,
                        percent_change
                    ])

                    file.flush()

                    print(
                        f"{timestamp.strftime('%H:%M:%S')} | "
                        f"Price: {price}"
                    )

                    break

            time.sleep(1)

        except Exception as e:

            print(e)

            time.sleep(3)