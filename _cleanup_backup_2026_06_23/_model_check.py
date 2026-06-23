import sys, os
sys.path.insert(0, 'C:/Users/marko/Desktop/Reymen Proje/hermes_projesi')
os.chdir('C:/Users/marko/Desktop/Reymen Proje/hermes_projesi')
try:
    from dotenv import load_dotenv
    load_dotenv('C:/Users/marko/AppData/Local/hermes/.env', override=True)
    load_dotenv('C:/Users/marko/AppData/Local/hermes/profiles/reymen/.env', override=True)
except Exception:
    pass
from reymen_launcher import _mevcut_model, _MODELLER

model, prov = _mevcut_model()
print("Aktif model :", model)
print("Provider    :", prov)
print()
print("Model listesi (secenekler):")
for i, (p, m, ad, env) in enumerate(_MODELLER, 1):
    key_ok = bool(not env or os.environ.get(env, "").strip())
    aktif  = (m == model and p == prov)
    durum  = "<-- AKTiF" if aktif else ""
    key_s  = "KEY:VAR" if key_ok else "KEY:YOK"
    print(f"  [{i}] {ad:<25} {m:<35} {key_s}  {durum}")
