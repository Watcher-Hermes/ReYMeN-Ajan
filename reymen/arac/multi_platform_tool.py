# -*- coding: utf-8 -*-
"""
multi_platform_tool.py — Çoklu platform mesajlaşma aracı.

Hermes Agent multi-platform karşılığı.
Telegram, Discord, Slack, SMS platformlarına mesaj gönderir.

Dosya: .ReYMeN/platforms.json

Kullanım:
    from reymen.arac.multi_platform_tool import PlatformManager
    mgr = PlatformManager()
    mgr.gonder("telegram", "chat_id", "Merhaba!")
    mgr.dagit("Tüm platformlara gönder", ["telegram", "discord"])
"""

import json
import os
import urllib.request
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class PlatformManager:
    """Çoklu platform mesaj yöneticisi."""

    def __init__(self, dosya: Optional[str] = None):
        self._dosya = Path(dosya) if dosya else (
            Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "platforms.json"
        )
        self._dosya.parent.mkdir(parents=True, exist_ok=True)
        self._platformlar: Dict[str, Dict] = {}
        self._gecmis: List[Dict] = []
        self._yukle()

    def _yukle(self):
        """Platform bilgilerini yükler."""
        if self._dosya.exists():
            try:
                data = json.loads(self._dosya.read_text(encoding="utf-8"))
                self._platformlar = data.get("platformlar", {})
                self._gecmis = data.get("gecmis", [])
            except Exception:
                self._varsayilan_olustur()
        else:
            self._varsayilan_olustur()

    def _varsayilan_olustur(self):
        """Varsayılan platform yapılandırması."""
        self._platformlar = {
            "telegram": {
                "aktif": True,
                "tip": "bot",
                "token_env": "TELEGRAM_BOT_TOKEN",
                "varsayilan_chat": "",
                "emoji": "📱",
            },
            "discord": {
                "aktif": False,
                "tip": "webhook",
                "webhook_url_env": "DISCORD_WEBHOOK_URL",
                "varsayilan_chat": "",
                "emoji": "🎮",
            },
            "slack": {
                "aktif": False,
                "tip": "webhook",
                "webhook_url_env": "SLACK_WEBHOOK_URL",
                "varsayilan_chat": "",
                "emoji": "💬",
            },
            "sms": {
                "aktif": False,
                "tip": "api",
                "provider": "twilio",
                "api_env": "TWILIO_API_KEY",
                "varsayilan_chat": "",
                "emoji": "📲",
            },
        }
        self._kaydet()

    def _kaydet(self):
        """Platform bilgilerini kaydeder."""
        self._gecmis = self._gecmis[-500:]
        data = {"platformlar": self._platformlar, "gecmis": self._gecmis}
        self._dosya.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str),
                               encoding="utf-8")

    def telegram_gonder(self, chat_id: str, mesaj: str, token: Optional[str] = None) -> Dict:
        """Telegram'a mesaj gönderir."""
        token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token:
            return {"ok": False, "error": "TELEGRAM_BOT_TOKEN bulunamadı."}

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": mesaj[:4096],
            "parse_mode": "Markdown",
        }).encode("utf-8")

        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
                return {"ok": True, "message_id": result.get("result", {}).get("message_id"),
                        "platform": "telegram"}
        except Exception as e:
            return {"ok": False, "error": f"Telegram hatası: {e}"}

    def discord_gonder(self, mesaj: str, webhook_url: Optional[str] = None) -> Dict:
        """Discord webhook ile mesaj gönderir."""
        webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")
        if not webhook_url:
            return {"ok": False, "error": "DISCORD_WEBHOOK_URL bulunamadı."}

        payload = json.dumps({"content": mesaj[:2000]}).encode("utf-8")

        try:
            req = urllib.request.Request(webhook_url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return {"ok": True, "platform": "discord"}
        except Exception as e:
            return {"ok": False, "error": f"Discord hatası: {e}"}

    def slack_gonder(self, mesaj: str, webhook_url: Optional[str] = None) -> Dict:
        """Slack webhook ile mesaj gönderir."""
        webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
        if not webhook_url:
            return {"ok": False, "error": "SLACK_WEBHOOK_URL bulunamadı."}

        payload = json.dumps({"text": mesaj[:4000]}).encode("utf-8")

        try:
            req = urllib.request.Request(webhook_url, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return {"ok": True, "platform": "slack"}
        except Exception as e:
            return {"ok": False, "error": f"Slack hatası: {e}"}

    def gonder(self, platform: str, chat_id: str, mesaj: str, **kwargs) -> Dict:
        """
        Platforma mesaj gönderir.

        Args:
            platform: telegram/discord/slack/sms
            chat_id: Alıcı ID (Discord/Slack webhook'ta gerekmez)
            mesaj: Mesaj içeriği

        Returns:
            {"ok": True/False, "platform": "...", "error": "..."}
        """
        if platform not in self._platformlar:
            return {"ok": False, "error": f"Bilinmeyen platform: {platform}"}

        if not self._platformlar[platform].get("aktif"):
            return {"ok": False, "error": f"Platform pasif: {platform}"}

        if platform == "telegram":
            sonuc = self.telegram_gonder(chat_id, mesaj, **kwargs)
        elif platform == "discord":
            sonuc = self.discord_gonder(mesaj, **kwargs)
        elif platform == "slack":
            sonuc = self.slack_gonder(mesaj, **kwargs)
        else:
            sonuc = {"ok": False, "error": f"Platform desteklenmiyor: {platform}"}

        # Geçmişe ekle
        self._gecmis.append({
            "platform": platform,
            "chat_id": chat_id,
            "mesaj": mesaj[:100],
            "sonuc": sonuc.get("ok", False),
            "zaman": datetime.now().isoformat(),
        })
        self._kaydet()

        return sonuc

    def dagit(self, mesaj: str, platformlar: Optional[List[str]] = None,
              chat_ids: Optional[Dict[str, str]] = None) -> Dict:
        """
        Birden fazla platforma mesaj gönderir.

        Args:
            mesaj: Mesaj içeriği
            platformlar: Hedef platform listesi (None = tüm aktif)
            chat_ids: Platform bazlı chat ID'leri

        Returns:
            {"sonuclar": {platform: result}, "basarili": N, "basarisiz": N}
        """
        hedefler = platformlar or [p for p, v in self._platformlar.items() if v.get("aktif")]
        chat_ids = chat_ids or {}

        sonuclar = {}
        basarili = 0
        basarisiz = 0

        for platform in hedefler:
            chat_id = chat_ids.get(platform, self._platformlar.get(platform, {}).get("varsayilan_chat", ""))
            r = self.gonder(platform, chat_id, mesaj)
            sonuclar[platform] = r
            if r.get("ok"):
                basarili += 1
            else:
                basarisiz += 1

        return {"sonuclar": sonuclar, "basarili": basarili, "basarisiz": basarisiz}

    def platform_ekle(self, ad: str, tip: str = "webhook", aktif: bool = True, **kwargs) -> Dict:
        """Yeni platform ekler."""
        self._platformlar[ad] = {"aktif": aktif, "tip": tip, **kwargs}
        self._kaydet()
        return {"ok": True, "platform": ad}

    def platform_guncelle(self, ad: str, **kwargs) -> Dict:
        """Platform bilgilerini günceller."""
        if ad not in self._platformlar:
            return {"ok": False, "error": f"Platform bulunamadı: {ad}"}
        self._platformlar[ad].update(kwargs)
        self._kaydet()
        return {"ok": True, "platform": ad}

    def listele(self) -> List[Dict]:
        """Tüm platformları listeler."""
        return [{"ad": ad, **bilgi} for ad, bilgi in self._platformlar.items()]

    def formatla(self) -> str:
        """Platformları okunabilir format döner."""
        satirlar = ["📋 Platformlar:\n"]
        for ad, bilgi in self._platformlar.items():
            emoji = bilgi.get("emoji", "❓")
            durum = "✅ Aktif" if bilgi.get("aktif") else "⏸️ Pasif"
            satirlar.append(f"{emoji} {ad} | {durum} | Tip: {bilgi.get('tip', '?')}")
        return "\n".join(satirlar)


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_mgr = None

def _get_mgr() -> PlatformManager:
    global _mgr
    if _mgr is None:
        _mgr = PlatformManager()
    return _mgr


def run(islem: str = "listele", platform: str = "", chat_id: str = "",
        mesaj: str = "", platformlar: str = "", ad: str = "",
        tip: str = "", webhook_url: str = "") -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: gonder/dagit/listele/ekle/guncelle
    """
    mgr = _get_mgr()

    if islem == "gonder":
        if not platform or not mesaj:
            return "[Hata]: platform ve mesaj gerekli."
        r = mgr.gonder(platform, chat_id, mesaj)
        return f"✅ {platform}'a gönderildi." if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "dagit":
        if not mesaj:
            return "[Hata]: mesaj gerekli."
        pl = [p.strip() for p in platformlar.split(",") if p.strip()] if platformlar else None
        r = mgr.dagit(mesaj, platformlar=pl)
        return f"📡 Dağıtım: {r['basarili']} başarılı, {r['basarisiz']} başarısız."

    elif islem == "ekle":
        if not ad:
            return "[Hata]: ad gerekli."
        r = mgr.platform_ekle(ad, tip=tip or "webhook")
        return f"✅ Platform eklendi: {ad}"

    elif islem == "guncelle":
        if not ad:
            return "[Hata]: ad gerekli."
        kwargs = {}
        if webhook_url:
            kwargs["webhook_url"] = webhook_url
        r = mgr.platform_guncelle(ad, **kwargs)
        return f"✅ Platform güncellendi: {ad}" if r["ok"] else f"[Hata]: {r['error']}"

    else:  # listele
        return mgr.formatla()


if __name__ == "__main__":
    import sys
    print(run(islem=sys.argv[1] if len(sys.argv) > 1 else "listele"))
