# Terminal Bloke Alternatifleri

## 1. execute_code + os.walk (Dosya Tarama)
```python
import os
for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".py"):
            fp = os.path.join(root, f)
            with open(fp, "r") as fh:
                content = fh.read()
```

## 2. execute_code + ast.parse (Kod Analizi)
```python
import ast
with open("dosya.py", "r") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(node.name, node.lineno)
```

## 3. execute_code + open() (Dosya Yazma)
```python
# write_file timeout atar, bunun yerine:
with open("hedef_yol.md", "w") as f:
    f.write("içerik")
# Büyük dosyayı 50 satırda böl:
# Part 1: birinci open("...", "w")
# Part 2: ikinci open("...", "a") ile append
```

## 4. execute_code + subprocess (Test Çalıştırma)
```python
import subprocess, sys
result = subprocess.run(
    [sys.executable, "-m", "pytest", "test.py", "-v"],
    capture_output=True, text=True, timeout=30
)
print(result.stdout)
```

## 5. execute_code + sys.path.insert (Import Test)
```python
import sys
sys.path.insert(0, "/proje/yolu")
from modul import fonksiyon
assert callable(fonksiyon)
```
