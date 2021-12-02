"""
This Tutorial shows how to create Binance API signature using HMAC and SHA256 Hashing Algorithm
Coded By: Omar Ghoneim
Watch the video here: https://youtu.be/WSv6Q-XhAy4
"""
import requests
from datetime import datetime
import API
import hmac
from urllib.parse import urlencode
import hashlib

public = API.P_key
secret = API.S_key


base_url = "https://api.binance.com"
endpoint = "/api/v3/order"
url = base_url + endpoint
timestamp = int(datetime.now().timestamp()) * 1000
payload = {
    "symbol": "ETHUSDT",
    "orderId": 6638849202,
    "timestamp": timestamp,
}

headers = {"X-MBX-APIKEY": public}
query_string = urlencode(payload)
payload["signature"] = hmac.new(
    secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
).hexdigest()

r = requests.delete(url, headers=headers, params=payload)
print(r.json())
