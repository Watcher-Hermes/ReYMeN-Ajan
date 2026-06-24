import base64
import os

# Read base64 encoded key from file
key_file = os.path.join(os.path.expanduser("~"), ".xiaomi_key_b64")
if not os.path.exists(key_file):
    print("ERROR: Key file not found")
    exit(1)

with open(key_file) as f:
    b64 = f.read().strip()

key = base64.b64decode(b64).decode()
line = "XIAOMI_API_KEY=" + key

env_path = ".env"
with open(env_path, 'r') as f:
    lines = f.readlines()

lines = [l for l in lines if not l.startswith('XIAOMI_API_KEY')]
lines.append("\n" + line + "\n")

with open(env_path, 'w') as f:
    f.writelines(lines)

print("OK len=" + str(len(key)))
