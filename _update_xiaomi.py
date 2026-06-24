import base64
key_b64 = "c2stc3lsMXZhb3VuMnNlNjU3djJlNXRlN3U4dzYwank3a2RqNDJodnB6bHlsNXpkdjRq"
key = base64.b64decode(key_b64).decode()
env_path = ".env"
with open(env_path, 'r') as f:
    lines = f.readlines()
lines = [l for l in lines if not l.startswith('XIAOMI_API_KEY')]
lines.append(f'\nXIAOMI_API_KEY={key}\n')
with open(env_path, 'w') as f:
    f.writelines(lines)
print(f"OK len={len(key)} bas={key[:7]} son={key[-4:]}")
