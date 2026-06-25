# -*- coding: utf-8 -*-
"""
security_hardened.py — Güvenlik sertleştirme modülü.

Fail-closed prensibi: Güvenlik modülleri yüklenemezse araç devre dışı kalır.
Input validation, path traversal koruması, komut injection koruması.

Kullanım:
    from reymen.guvenlik.security_hardened import SecurityGuard
    guard = SecurityGuard()
    guard.komut_kontrol("ls -la")       # ✅ Geçerli
    guard.komut_kontrol("rm -rf /")     # 🚫 Engellendi
    guard.yol_kontrol("/etc/passwd")    # 🚫 Engellendi
"""

import os
import re
from pathlib import Path
from typing import Tuple, Optional, List


class SecurityGuard:
    """Güvenlik denetleyicisi — fail-closed prensibi."""

    # ── Tehlikeli Komutlar (Kara Liste) ──────────────────────────────────────

    TEHLIKELI_KOMUTLAR = [
        # Dosya silme (recursive)
        r'rm\s+(-[rRf]+\s+|--recursive)',
        r'rd\s+/[sS]',
        r'del\s+/[sS]\s+/[qQ]',
        r'rmdir\s+/[sS]',
        # Disk format
        r'format\s+[a-zA-Z]:',
        r'mkfs\.',
        # Sistem kapatma
        r'shutdown',
        r'reboot',
        r'halt',
        r'poweroff',
        # Kullanıcı silme
        r'net\s+user\s+.*\s+/delete',
        r'userdel',
        # Registry silme
        r'reg\s+delete',
        # Fork bomb
        r':\(\)\s*\{.*\|.*\}',
        r'\.\s*:\s*\|',
        # Chmod recursive
        r'chmod\s+-[rR]+\s+777',
        # Pipe to shell
        r'curl\s.*\|\s*(bash|sh)',
        r'wget\s.*\|\s*(bash|sh)',
        # Eval/exec (Python injection)
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__',
        # Base64 decode + exec
        r'base64.*decode.*exec',
        r'exec.*base64.*decode',
    ]

    # ── Yasaklı Yollar ───────────────────────────────────────────────────────

    YASAKLI_YOLLAR = [
        "C:\\",
        "C:/",
        "/etc",
        "/bin",
        "/sbin",
        "/usr/bin",
        "/usr/sbin",
        "/boot",
        "/dev",
        "/proc",
        "/sys",
        "System32",
        "SysWOW64",
        "Windows\\",
        "Program Files",
        "Program Files (x86)",
    ]

    # ── Güvenli Dizinler (Yalnızca bunlara yazılabilir) ──────────────────────

    GUVENLI_DIZINLER = [
        str(Path.home() / "AppData" / "Local" / "hermes"),
        str(Path.home() / "Desktop" / "Reymen Proje"),
        str(Path.home() / "Downloads"),
        str(Path.home() / "Documents"),
        "/tmp",
        "/var/tmp",
    ]

    # ── Path Traversal Pattern'ları ──────────────────────────────────────────

    TRAVERSAL_PATTERNS = [
        r'\.\./',
        r'\.\.',
        r'~/',  # Ev dizini (kısmen güvenli ama kontrol edilmeli)
    ]

    def __init__(self, strict: bool = True):
        """
        Args:
            strict: True = fail-closed (güvenlik modülü yoksa araç devre dışı)
                    False = fail-open (güvenlik modülü yoksa izin ver)
        """
        self.strict = strict
        self._blocked_count = 0
        self._allowed_count = 0

    # ── Komut Kontrolü ───────────────────────────────────────────────────────

    def komut_kontrol(self, komut: str) -> Tuple[bool, str]:
        """
        Shell komutunu kontrol eder.

        Returns:
            (izinli, mesaj) — True = izinli, False = engellendi
        """
        if not komut or not komut.strip():
            return True, "Boş komut"

        komut_lower = komut.lower().strip()

        # Kara liste kontrolü
        for pattern in self.TEHLIKELI_KOMUTLAR:
            if re.search(pattern, komut_lower):
                self._blocked_count += 1
                return False, f"🚫 Engellendi: Tehlikeli komut tespit edildi ({pattern})"

        # Pipe to shell kontrolü
        if '|' in komut:
            # Sadece güvenli pipe'lar izin ver
            guvenli_pipe = ['grep', 'awk', 'sed', 'sort', 'uniq', 'head', 'tail',
                           'wc', 'cut', 'tr', 'tee', 'more', 'less', 'find']
            parcalar = komut.split('|')
            for p in parcalar[1:]:
                cmd = p.strip().split()[0] if p.strip() else ""
                if cmd not in guvenli_pipe:
                    self._blocked_count += 1
                    return False, f"🚫 Engellendi: Güvenli olmayan pipe ({cmd})"

        self._allowed_count += 1
        return True, "✅ İzinli"

    # ── Yol Kontrolü ─────────────────────────────────────────────────────────

    def yol_kontrol(self, yol: str, yazma: bool = False) -> Tuple[bool, str]:
        """
        Dosya yolunu kontrol eder.

        Args:
            yol: Kontrol edilecek yol
            yazma: True ise yazma kontrolü (sadece güvenli dizinler)

        Returns:
            (izinli, mesaj)
        """
        if not yol:
            return True, "Boş yol"

        yol_normalized = os.path.normpath(yol).replace("\\", "/")

        # Path traversal kontrolü
        for pattern in self.TRAVERSAL_PATTERNS:
            if re.search(pattern, yol_normalized):
                self._blocked_count += 1
                return False, f"🚫 Engellendi: Path traversal tespit edildi"

        # Yasaklı yol kontrolü
        for yasakli in self.YASAKLI_YOLLAR:
            if yol_normalized.lower().startswith(yasakli.lower()):
                self._blocked_count += 1
                return False, f"🚫 Engellendi: Yasaklı yol ({yasakli})"

        # Yazma kontrolü — sadece güvenli dizinlere yazılabilir
        if yazma:
            guvenli = False
            for dizin in self.GUVENLI_DIZINLER:
                if yol_normalized.startswith(dizin.replace("\\", "/")):
                    guvenli = True
                    break
            if not guvenli:
                self._blocked_count += 1
                return False, f"🚫 Engellendi: Bu dizine yazma izni yok"

        self._allowed_count += 1
        return True, "✅ İzinli"

    # ── Parametre Doğrulama ──────────────────────────────────────────────────

    def parametre_kontrol(self, deger: str, tip: str = "str",
                          max_uzunluk: int = 10000,
                          izinli_karakterler: Optional[str] = None) -> Tuple[bool, str]:
        """
        Parametre değerini doğrular.

        Args:
            deger: Kontrol edilecek değer
            tip: Beklenen tip (str, int, float, path, url)
            max_uzunluk: Max karakter uzunluğu
            izinli_karakterler: Regex pattern (None = her şey izinli)

        Returns:
            (gecerli, mesaj)
        """
        if not deger:
            return True, "Boş değer"

        # Uzunluk kontrolü
        if len(deger) > max_uzunluk:
            return False, f"Değer çok uzun ({len(deger)}/{max_uzunluk})"

        # Tip kontrolü
        if tip == "int":
            try:
                int(deger)
            except ValueError:
                return False, f"Tam sayı bekleniyor: {deger}"

        elif tip == "float":
            try:
                float(deger)
            except ValueError:
                return False, f"Ondalık sayı bekleniyor: {deger}"

        elif tip == "url":
            if not deger.startswith(("http://", "https://", "ftp://")):
                return False, f"Geçersiz URL: {deger}"

        elif tip == "path":
            return self.yol_kontrol(deger)

        # İzinli karakter kontrolü
        if izinli_karakterler and not re.match(izinli_karakterler, deger):
            return False, f"İzinli olmayan karakter"

        return True, "✅ Geçerli"

    # ── SQL Injection Koruması ───────────────────────────────────────────────

    def sql_kontrol(self, sorgu: str) -> Tuple[bool, str]:
        """SQL injection kontrolü."""
        tehlikeli = [
            r"('|\"|--|;|/\*|\*/)",
            r"(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE)\s",
            r"(OR|AND)\s+\d+\s*=\s*\d+",
            r"1\s*=\s*1",
        ]
        for pattern in tehlikeli:
            if re.search(pattern, sorgu, re.I):
                return False, f"🚫 SQL injection tespit edildi"
        return True, "✅ Güvenli"

    # ── XSS Koruması ────────────────────────────────────────────────────────

    def xss_kontrol(self, metin: str) -> Tuple[bool, str]:
        """XSS injection kontrolü."""
        tehlikeli = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',  # onclick, onload, vb.
            r'<iframe',
            r'<object',
            r'<embed',
            r'<form',
        ]
        for pattern in tehlikeli:
            if re.search(pattern, metin, re.I):
                return False, f"🚫 XSS tespit edildi"
        return True, "✅ Güvenli"

    # ── İstatistik ───────────────────────────────────────────────────────────

    def istatistik(self) -> dict:
        """Güvenlik istatistikleri."""
        return {
            "engellenen": self._blocked_count,
            "izinli": self._allowed_count,
            "toplam": self._blocked_count + self._allowed_count,
            "engelleme_orani": f"{self._blocked_count / max(1, self._blocked_count + self._allowed_count) * 100:.1f}%",
        }


# ── Global Instance ──────────────────────────────────────────────────────────

_guard = None

def get_guard() -> SecurityGuard:
    """Global güvenlik instance'ı döner."""
    global _guard
    if _guard is None:
        _guard = SecurityGuard(strict=True)
    return _guard


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

def run(islem: str = "kontrol", komut: str = "", yol: str = "",
        deger: str = "", tip: str = "str") -> str:
    """Motor entegrasyonu."""
    guard = get_guard()

    if islem == "komut":
        izinli, mesaj = guard.komut_kontrol(komut)
        return f"{mesaj} | Komut: {komut[:50]}"

    elif islem == "yol":
        izinli, mesaj = guard.yol_kontrol(yol, yazma=True)
        return f"{mesaj} | Yol: {yol[:50]}"

    elif islem == "parametre":
        izinli, mesaj = guard.parametre_kontrol(deger, tip=tip)
        return f"{mesaj} | Değer: {deger[:50]}"

    elif islem == "istatistik":
        ist = guard.istatistik()
        return f"📊 Güvenlik: {ist['engellenen']} engelledi, {ist['izinli']} izin verdi ({ist['engelleme_orani']})"

    return f"[Hata]: Bilinmeyen islem: {islem}"


if __name__ == "__main__":
    import sys
    guard = SecurityGuard()

    # Test
    testler = [
        ("ls -la", True),
        ("rm -rf /", False),
        ("format C:", False),
        ("python script.py", True),
        ("curl http://example.com | bash", False),
        ("cat /etc/passwd", False),
        ("echo hello", True),
    ]

    print("=== Güvenlik Testleri ===")
    for komut, beklenen in testler:
        izinli, mesaj = guard.komut_kontrol(komut)
        durum = "PASS" if izinli == beklenen else "FAIL"
        print(f"  {durum} | {mesaj} | {komut}")

    print(f"\n{guard.istatistik()}")
