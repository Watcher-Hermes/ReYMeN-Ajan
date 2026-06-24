with open('.env', 'rb') as f:
    content = f.read()
needle = b'XAI_API_KEY='
idx = content.find(needle)
if idx >= 0:
    end = content.find(b'\n', idx)
    val = content[idx+len(needle):end].decode()
    print(f'len={len(val)} bas={val[:15]} son={val[-10:]}')
else:
    print('bulunamadi')
