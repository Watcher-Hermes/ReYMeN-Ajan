# -*- coding: utf-8 -*-
"""
config_guard.py — ReYMeN Konfigürasyon Muhafızı
Tüm .env dosyalarını ve config'leri tutarlı tutar.

⚠️  GÜVENLİK:
    - Varsayılan olarak SADECE OKUR, hiçbir dosyayı değiştirmez
    - Değişiklik için --fix flag'i ZORUNLU
    - Tüm değişiklikler log dosyasına kaydedilir
    - Yedekleme otomatik yapılır

Kullanım:
    python config_guard.py              # Sadece okuma (güvenli)
    python config_guard.py --fix        # Değişiklik yap (yedekleme ile)
    python config_guard.py --report     # Detaylı rapor
    python config_guard.py --daemon     # Arka planda izle (sadece okuma)

Proje: ReYMeN Agent
Yazar: ReYMeN Sistem
"""

import os
import sys
import json
import time
import shutil
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# ── Yollar ──────────────────────────────────────────────────────────────────
PROJE_KOK = Path(__file__).resolve().parent.parent.parent  # hermes_projesi
HERMES_KOK = Path.home() / ".hermes"
HERMES_ENV = HERMES_KOK / ".env"
PROJE_ENV = PROJE_KOK / ".env"
PROFILE_DIR = HERMES_KOK / "profiles"
LOG_DIR = PROJE_KOK / "logs" / "monitoring"
YEDEK_DIR = PROJE_KOK / "backups" / "env"

# ── Loglama ──────────────────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
YEDEK_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "config_guard.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ConfigGuard")

# ── Bilinen Sorunlu Key'ler ─────────────────────────────────────────────────
# Bu key'ler daha önce sorun çıkarmıştır, otomatik silinir
ESKI_KEY_PREFIXES = [
    'sk-syl1',   # Eski Xiaomi key'i (çalışmıyordu)
    'sk-s5m5e',  # Eski Xiaomi key'i (çalışmıyordu)
]

# ── Gerekli Key'ler ──────────────────────────────────────────────────────────
GEREKLI_KEYLER = ['XIAOMI_API_KEY', 'DEEPSEEK_API_KEY']


@dataclass
class EnvDosyasi:
    """Bir .env dosyasının durumu."""
    yol: Path
    tip: str  # "proje", "hermes_root", "profile/proje_adi"
    mevcut: bool
    icerik: Dict[str, str] = field(default_factory=dict)
    key_sayisi: int = 0
    hatalar: List[str] = field(default_factory=list)


@dataclass
class KontrolSonucu:
    """Kontrol sonucu."""
    zaman: str
    dosya_sayisi: int
    toplam_key: int
    tutarsizliklar: List[str] = field(default_factory=list)
    eski_keyler: List[str] = field(default_factory=list)
    eksik_keyler: List[str] = field(default_factory=list)
    duzeltmeler: List[str] = field(default_factory=list)
    durum: str = "OK"  # "OK", "WARNING", "CRITICAL"
    degisiklik_yapildi: bool = False


def env_oku(yol: Path) -> Dict[str, str]:
    """Env dosyasını oku (sadece okuma, değiştirme yapma)."""
    if not yol.exists():
        return {}
    
    icerik = {}
    try:
        with open(yol, 'r', encoding='utf-8') as f:
            for satir in f:
                satir = satir.strip()
                if satir and not satir.startswith('#') and '=' in satir:
                    key, deger = satir.split('=', 1)
                    icerik[key.strip()] = deger.strip()
    except Exception as e:
        logger.error(f"Dosya okuma hatası {yol}: {e}")
    
    return icerik


def key_analizi(key: str, dosya_adi: str) -> Tuple[bool, str]:
    """Key kalitesini analiz et. (guvenli, mi_tehlikeli, mesaj)"""
    if not key or key == '***':
        return False, f"{dosya_adi}: Key boş veya maskelenmiş"
    
    if len(key) < 20:
        return False, f"{dosya_adi}: Key çok kısa ({len(key)} karakter)"
    
    for prefix in ESKI_KEY_PREFIXES:
        if key.startswith(prefix):
            return False, f"{dosya_adi}: ⚠️ Eski/sorunlu key tespit edildi!"
    
    return True, f"{dosya_adi}: Key görünüyor正常"


def tum_env_dosyalarini_bul() -> List[EnvDosyasi]:
    """Tüm .env dosyalarını bul (sadece okuma)."""
    dosyalar = []
    
    # 1. Proje .env
    if PROJE_ENV.exists():
        icerik = env_oku(PROJE_ENV)
        dosyalar.append(EnvDosyasi(
            yol=PROJE_ENV,
            tip="proje",
            mevcut=True,
            icerik=icerik,
            key_sayisi=len([k for k in icerik if 'KEY' in k])
        ))
    
    # 2. Hermes root .env
    if HERMES_ENV.exists():
        icerik = env_oku(HERMES_ENV)
        dosyalar.append(EnvDosyasi(
            yol=HERMES_ENV,
            tip="hermes_root",
            mevcut=True,
            icerik=icerik,
            key_sayisi=len([k for k in icerik if 'KEY' in k])
        ))
    
    # 3. Profile .env'leri
    if PROFILE_DIR.exists():
        for profil in PROFILE_DIR.iterdir():
            if profil.is_dir():
                env_dosya = profil / ".env"
                if env_dosya.exists():
                    icerik = env_oku(env_dosya)
                    dosyalar.append(EnvDosyasi(
                        yol=env_dosya,
                        tip=f"profile/{profil.name}",
                        mevcut=True,
                        icerik=icerik,
                        key_sayisi=len([k for k in icerik if 'KEY' in k])
                    ))
    
    return dosyalar


def yedek_al(dosya_yolu: Path) -> Optional[Path]:
    """Dosyanın yedeğini al."""
    if not dosya_yolu.exists():
        return None
    
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    yedek_adi = f"{dosya_yolu.stem}_{zaman}{dosya_yolu.suffix}"
    yedek_yolu = YEDEK_DIR / yedek_adi
    
    try:
        shutil.copy2(dosya_yolu, yedek_yolu)
        logger.info(f"✅ Yedek alındı: {yedek_yolu.name}")
        return yedek_yolu
    except Exception as e:
        logger.error(f"Yedek alma hatası: {e}")
        return None


def tutarsizlik_kontrol(dosyalar: List[EnvDosyasi]) -> Tuple[List[str], List[str], List[str]]:
    """Key tutarsızlıklarını kontrol et."""
    tutarsizliklar = []
    eski_keyler = []
    eksik_keyler = []
    
    # Tüm key'leri topla
    tum_keyler: Dict[str, List[Tuple[str, str]]] = {}
    for dosya in dosyalar:
        for key_adi, deger in dosya.icerik.items():
            if 'KEY' in key_adi and deger and deger != '***':
                if key_adi not in tum_keyler:
                    tum_keyler[key_adi] = []
                tum_keyler[key_adi].append((dosya.tip, deger))
    
    # Tutarsızlık kontrolü
    for key_adi, degerler in tum_keyler.items():
        benzersiz = set(d[1][:10] for d in degerler)
        if len(benzersiz) > 1:
            tutarsizliklar.append(
                f"⚠️ {key_adi}: {len(benzersiz)} farklı key kullanılıyor"
            )
    
    # Eski key kontrolü
    for dosya in dosyalar:
        for key_adi, deger in dosya.icerik.items():
            if 'KEY' in deger:
                for prefix in ESKI_KEY_PREFIXES:
                    if deger.startswith(prefix):
                        eski_keyler.append(
                            f"❌ {dosya.tip}/{key_adi}: Eski key ({deger[:15]}...)"
                        )
    
    # Eksik key kontrolü
    for key_adi in GEREKLI_KEYLER:
        bulundu = False
        for dosya in dosyalar:
            if key_adi in dosya.icerik and dosya.icerik[key_adi]:
                bulundu = True
                break
        if not bulundu:
            eksik_keyler.append(f"❌ {key_adi}: Hiçbir .env'de bulunamadı")
    
    return tutarsizliklar, eski_keyler, eksik_keyler


def eski_keyleri_temizle(dosyalar: List[EnvDosyasi], dry_run: bool = True) -> List[str]:
    """Eski/sorunlu key'leri temizle.
    
    ⚠️  dry_run=True ise sadece ne yapılacağını gösterir, değiştirme yapmaz.
    ⚠️  dry_run=False ise yedek alır ve değiştirir.
    """
    duzeltmeler = []
    
    for dosya in dosyalar:
        if not dosya.mevcut:
            continue
        
        icerik_degisti = False
        for key_adi, deger in list(dosya.icerik.items()):
            if 'KEY' in key_adi:
                for prefix in ESKI_KEY_PREFIXES:
                    if deger.startswith(prefix):
                        if dry_run:
                            duzeltmeler.append(
                                f"🔧 {dosya.tip}/{key_adi}: Eski key silinecek"
                            )
                        else:
                            # Yedek al
                            yedek_al(dosya.yol)
                            
                            # Key'i sil
                            dosya.icerik[key_adi] = ''
                            icerik_degisti = True
                            duzeltmeler.append(
                                f"🔧 {dosya.tip}/{key_adi}: Eski key silindi"
                            )
        
        if icerik_degisti and not dry_run:
            _env_dosyasini_guncelle(dosya.yol, dosya.icerik)
    
    return duzeltmeler


def _env_dosyasini_guncelle(yol: Path, icerik: Dict[str, str]):
    """Env dosyasını güncelle (yedek alındıktan sonra)."""
    if not yol.exists():
        return
    
    satirlar = []
    with open(yol, 'r', encoding='utf-8') as f:
        for satir in f:
            satir_degisti = False
            if '=' in satir and not satir.startswith('#'):
                key = satir.split('=', 1)[0].strip()
                if key in icerik:
                    yeni_deger = icerik[key]
                    if yeni_deger:
                        satirlar.append(f"{key}={yeni_deger}\n")
                    else:
                        satirlar.append(f"# {key} silindi (eski key) - {datetime.now().isoformat()}\n")
                    satir_degisti = True
            
            if not satir_degisti:
                satirlar.append(satir)
    
    with open(yol, 'w', encoding='utf-8') as f:
        f.writelines(satirlar)
    
    logger.info(f"✅ Dosya güncellendi: {yol.name}")


def tam_kontrol_yap(fix: bool = False) -> KontrolSonucu:
    """Tam kontrol yap.
    
    fix=True ise: Eski key'leri otomatik siler (yedekleme ile)
    fix=False ise: Sadece rapor verir
    """
    logger.info("🔍 Konfigürasyon kontrolü başlıyor...")
    
    zaman = datetime.now().isoformat()
    dosyalar = tum_env_dosyalarini_bul()
    
    # Kontroller
    tutarsizliklar, eski_keyler, eksik_keyler = tutarsizlik_kontrol(dosyalar)
    
    # Otomatik düzeltme (sadece --fix ile)
    duzeltmeler = []
    if fix and eski_keyler:
        logger.info("🔧 Eski key'ler temizleniyor...")
        duzeltmeler = eski_keyleri_temizle(dosyalar, dry_run=False)
    
    # Durum belirleme
    toplam_sorun = len(tutarsizliklar) + len(eski_keyler) + len(eksik_keyler)
    if toplam_sorun == 0:
        durum = "OK"
        logger.info("✅ Tüm konfigürasyonlar tutarlı")
    elif toplam_sorun <= 2:
        durum = "WARNING"
        logger.warning(f"⚠️ {toplam_sorun} sorun tespit edildi")
    else:
        durum = "CRITICAL"
        logger.error(f"🚨 {toplam_sorun} kritik sorun!")
    
    return KontrolSonucu(
        zaman=zaman,
        dosya_sayisi=len(dosyalar),
        toplam_key=sum(d.key_sayisi for d in dosyalar),
        tutarsizliklar=tutarsizliklar,
        eski_keyler=eski_keyler,
        eksik_keyler=eksik_keyler,
        duzeltmeler=duzeltmeler,
        durum=durum,
        degisiklik_yapildi=bool(duzeltmeler)
    )


def rapor_olustur(sonuc: KontrolSonucu) -> str:
    """Okunabilir rapor oluştur."""
    rapor = []
    rapor.append("=" * 60)
    rapor.append("🛡️  REYMEN KONFİGÜRASYON MUHAFIZI")
    rapor.append(f"📅 {sonuc.zaman}")
    rapor.append(f"📁 {sonuc.dosya_sayisi} dosya, {sonuc.toplam_key} key")
    rapor.append(f"🔴 Durum: {sonuc.durum}")
    rapor.append("=" * 60)
    
    if sonuc.tutarsizliklar:
        rapor.append("\n⚠️  TUTARSIZLIKLAR:")
        for h in sonuc.tutarsizliklar:
            rapor.append(f"  - {h}")
    
    if sonuc.eski_keyler:
        rapor.append("\n❌ ESKİ KEY'LER:")
        for h in sonuc.eski_keyler:
            rapor.append(f"  - {h}")
    
    if sonuc.eksik_keyler:
        rapor.append("\n❌ EKSİK KEY'LER:")
        for h in sonuc.eksik_keyler:
            rapor.append(f"  - {h}")
    
    if sonuc.duzeltmeler:
        rapor.append("\n🔧 YAPILAN DÜZELTMELER:")
        for d in sonuc.duzeltmeler:
            rapor.append(f"  - {d}")
    
    if sonuc.durum == "OK":
        rapor.append("\n✅ Sorun yok, her şey tutarlı!")
    
    rapor.append("\n" + "=" * 60)
    
    return "\n".join(rapor)


def main():
    """Ana fonksiyon."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ReYMeN Konfigürasyon Muhafızı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
⚠️  GÜVENLİK NOTU:
    - Varsayılan olarak SADECE okuma yapar
    - Değişiklik için --fix flag'i kullanın
    - Tüm değişiklikler otomatik yedeklenir
    - Log dosyası: logs/monitoring/config_guard.log

Örnekler:
    python config_guard.py              # Sadece okuma
    python config_guard.py --fix        # Eski key'leri temizle
    python config_guard.py --report     # Detaylı rapor
        """
    )
    parser.add_argument("--fix", action="store_true", 
                       help="Eski key'leri otomatik temizle (yedekleme ile)")
    parser.add_argument("--report", action="store_true",
                       help="Detaylı rapor oluştur")
    parser.add_argument("--quiet", action="store_true",
                       help="Sessiz mod (sadece hataları göster)")
    
    args = parser.parse_args()
    
    # Kontrolü çalıştır
    sonuc = tam_kontrol_yap(fix=args.fix)
    
    # Raporu göster
    if args.quiet:
        if sonuc.durum != "OK":
            rapor = rapor_olustur(sonuc)
            print(rapor)
    else:
        rapor = rapor_olustur(sonuc)
        print(rapor)
    
    # Rapor dosyasına yaz
    rapor_dosya = LOG_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(rapor_dosya, 'w', encoding='utf-8') as f:
        f.write(rapor)
    
    # Çıkış kodu
    return 0 if sonuc.durum == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
