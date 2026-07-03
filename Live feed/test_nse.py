#Om Namo Venketesaya
import requests



headers = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()

# Visit homepage first
session.get(
    "https://www.nseindia.com",
    headers=headers
)

# Fetch quote
response = session.get(
    "https://www.nseindia.com/api/allIndices",
    headers=headers
)

print(response.status_code)

data = response.json()

for item in data["data"]:
    if item["index"] == "NIFTY 50":
        print(item)
        break