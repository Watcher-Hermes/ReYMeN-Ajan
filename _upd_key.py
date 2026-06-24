import base64
import sys

# Read key from command line argument
if len(sys.argv) < 2:
    print("Usage: python _upd_key.py <base64_key>")
    sys.exit(1)

b64 = sys.argv[1]
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
