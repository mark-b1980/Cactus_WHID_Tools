import requests
import time

url = "http://192.168.1.1/runlivepayload"
delay = int(input("DELAY BETWEEN MOVEMENTS IN SEC.> "))

while True:
    print("Jiggeling...")
    res = requests.post(url, data={"livepayload": 'DefaultDelay:350\nMouseMoveUp:1\nMouseMoveDown:1', "livepayloadpresent": "1"})
    time.sleep(delay)

