import base64
import sys
import os

chunk_size = 1500

def usage():
    print(f"\nUSAGE:\n------\n{os.path.basename(__file__)} [LOCAL FILEPATH] [REMOTE FILEPATH]\n")
    quit()

# CHECK CMD-LINE ARGS
if len(sys.argv) != 3:
    usage()
else:
    file = sys.argv[1]
    remote = sys.argv[2]

with open(file, "rb") as f:
    data = f.read()
    b64 = base64.b64encode(data).decode("UTF-8")

# Split into Base64 encoded string into chunks 
chunks = [b64[i:i+chunk_size] for i in range(0, len(b64), chunk_size)]

# Write payload
with open(os.path.basename(file) + ".txt", "w") as f:
    f.write("PrintLine:$b=\"\"\n")
    for chunk in chunks:
        f.write(f"PrintLine:$b+=\"{chunk}\"\n")
    f.write(f"PrintLine:[IO.File]::WriteAllBytes(\"{remote}\", [Convert]::FromBase64String($b));")
