"""
ReYMeN Agent — Profil .env Validator
Her profile .env'de gerekli API key'leri kontrol eder.
Eksikse uyarır, çalışma zamanında hata oluşmaması için.
"""
import os
import sys
from pathlib import Path

HERMES_PROFILES = Path.home() / "AppData/Local/hermes/profiles"
PROJE_DIZINI = Path.home() / "Desktop/Reymen Proje/hermes_projesi"

# Her profil için beklenen key'ler (provider config'e göre)
PROFIL_BEKLENEN = {
    "kiral38": {
        "gerekli": ["DEEPSEEK_API_KEY"],
        "opsiyonel": ["OPENROUTER_API_KEY", "TELEGRAM_BOT_TOKEN"],
    },
    "reymen": {
        "gerekli": ["DEEPSEEK_API_KEY"],
        "opsiyonel": ["TELEGRAM_BOT_TOKEN"],
    },
    "default": {
        "gerekli": ["DEEPSEEK_API_KEY"],
        "opsiyonel": ["TELEGRAM_BOT_TOKEN"],
    },
}

PROFIL_CONFIG = {
    "kiral38": {
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com",
        "fallback": "openrouter"
    },
    "reymen": {
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com"
    },
    "default": {
        "provider": "deepseek",
        "base_url": "https://api.deepseek.com"
    }
}


def kontrol_et():
    """Tüm profilleri tara, eksikleri raporla."""
    sorunlar = []
    uyarilar = []
    
    for profil, beklenen in PROFIL_BEKLENEN.items():
        env_yolu = HERMES_PROFILES / profil / ".env"
        
        if not env_yolu.exists():
            sorunlar.append(f"[{profil}] .env dosyası YOK")
            continue
        
        # .env'yi oku
        env_deg = {}
        with open(env_yolu, "r", encoding="utf-8-sig") as f:
            for satir in f:
                satir = satir.strip()
                if "=" in satir and not satir.startswith("#"):
                    anahtar, deger = satir.split("=", 1)
                    env_deg[anahtar.strip()] = deger.strip()
        
        # Gerekli key'leri kontrol et
        for key in beklenen["gerekli"]:
            if key not in env_deg or not env_deg[key] or env_deg[key].startswith("***"):
                sorunlar.append(f"[{profil}] {key} eksik veya maskelenmiş")
        
        # Opsiyonel key'leri kontrol et
        for key in beklenen["opsiyonel"]:
            if key not in env_deg or not env_deg[key]:
                uyarilar.append(f"[{profil}] {key} tanımlı değil (opsiyonel)")
        
        # provider base_url kontrolü
        config = PROFIL_CONFIG.get(profil, {})
        if config.get("base_url"):
            # Config'te boş base_url var mı? Varsa uyar
            cfg_yolu = HERMES_PROFILES / profil / "config.yaml"
            if cfg_yolu.exists():
                with open(cfg_yolu, "r", encoding="utf-8") as f:
                    cfg = f.read()
                if f"base_url: ''" in cfg or f"base_url: \"\"" in cfg:
                    uyarilar.append(
                        f"[{profil}] config.yaml'de base_url BOŞ! "
                        f"Beklenen: {config['base_url']}. "
                        f"DeepSeek API çağrıları çalışmayabilir."
                    )
    
    return sorunlar, uyarilar


def raporla():
    """Raporu yazdır."""
    sorunlar, uyarilar = kontrol_et()
    
    print("=" * 60)
    print("🔍 ReYMeN Profil .env Validator")
    print("=" * 60)
    
    if not sorunlar and not uyarilar:
        print("\n✅ Tüm profiller temiz. Her şey yolunda.")
        return True
    
    if sorunlar:
        print(f"\n❌ {len(sorunlar)} KRİTİK SORUN:")
        for s in sorunlar:
            print(f"   • {s}")
    
    if uyarilar:
        print(f"\n⚠️  {len(uyarilar)} UYARI:")
        for u in uyarilar:
            print(f"   • {u}")
    
    print(f"\n📋 Özet: {len(sorunlar)} sorun, {len(uyarilar)} uyarı")
    return len(sorunlar) == 0


def duzelt_base_url():
    """
    base_url boş olan profilleri düzelt.
    Dry-run: ne yapılacağını göster.
    """
    print("\n🛠  Düzeltme Önerileri:")
    for profil, config in PROFIL_CONFIG.items():
        cfg_yolu = HERMES_PROFILES / profil / "config.yaml"
        if cfg_yolu.exists() and config.get("base_url"):
            print(f"\n   [{profil}] config.yaml → base_url: {config['base_url']}")
            print(f"          Öneri: base_url manuel eklenmeli")

    print("\n   Elle düzeltme:")
    print("   hermes config set model.base_url https://api.deepseek.com")


if __name__ == "__main__":
    tamam = raporla()
    if not tamam:
        duzelt_base_url()
    sys.exit(0 if tamam else 1)
