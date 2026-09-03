# Om Namo Venketesaya

import csv
from datetime import datetime
import os
import time
from detector import EventDetector
import yfinance as yf


def main():
  detector = EventDetector()

  csv_file = "live_nifty_log.csv"

  # Check if file exists before opening in append ('a') mode
  file_exists = os.path.exists(csv_file)
  with open(csv_file, mode="a", newline="") as file:
    writer = csv.writer(file)
    # Only write header if creating a brand new file
    if not file_exists:
      writer.writerow(["Timestamp", "Price", "Confidence", "Alert_Triggered"])

  print("Logging data...")

  last_timestamp = None
  try:
    while True:

      nifty = yf.Ticker("^NSEI")

      data = nifty.history(
          period="1d", interval="1m"
      )  # last day , at 1m ontervals return pandas df

      if not data.empty:

        latest_row = data.iloc[-1]  # takes latest row
        current_timestamp = (
            data.index[-1]
        )  # this return a stimestamp object of pandas with the date and time

        if current_timestamp != last_timestamp:  # if new timestam
          current_price = latest_row["Close"]

          alert_triggered = detector.update(
              current_price
          )  # this feeds it into the EvenDetetcor

          time_str = current_timestamp.strftime("%H:%M:%S")
          print(
              f"[{time_str}] NIFTY: {current_price:.2f} | Conf:"
              f" {detector.confidence:.2f} | Alert: {alert_triggered}"
          )

          with open(csv_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                current_timestamp,
                current_price,
                detector.confidence,
                alert_triggered,
            ])

          last_timestamp = current_timestamp  # update the timestamp
      time.sleep(30)

  except KeyboardInterrupt:
    print("\n🛑 Live stream stopped safely. Data saved to:", csv_file)


if __name__ == "__main__":
  main()