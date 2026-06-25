# -*- coding: utf-8 -*-
"""Olay-güdümlü hook dispatcher.

Hermes'in ``invoke_hook`` sisteminden adapte edilmiştir. Konuşma döngüsü
belirli noktalarda hook'ları ateşler; yüklü plugin'ler bunları dinler.

Desteklenen hook olayları:
    on_session_start    — Oturum başlarken
    on_session_end      — Oturum biterken
    on_turn_start       — Her tur başında
    on_turn_end         — Her tur sonunda
    on_tool_call        — Araç çağrılmadan önce
    on_tool_result      — Araç sonucu alındıktan sonra
    on_error            — Hata oluştuğunda
    on_context_compress — Context sıkıştırılmadan önce
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, List, Optional

log = logging.getLogger("conversation_loop")

# Hook kayıt defteri: olay_adı → [callback_listesi]
_HOOK_KAYDI: Dict[str, List[Callable]] = {}

# Desteklenen olay adları
GECERLI_OLAYLAR = frozenset({
    "on_session_start",
    "on_session_end",
    "on_turn_start",
    "on_turn_end",
    "on_tool_call",
    "on_tool_result",
    "on_error",
    "on_context_compress",
})


def hook_kaydet(olay: str, callback: Callable) -> None:
    """Bir hook callback'i kaydet.

    Args:
        olay:     Hook olay adı (ör. "on_session_start").
        callback: Çağrılacak fonksiyon. Kwargs ile çağrılır.

    Raises:
        ValueError: Bilinmeyen olay adı.
    """
    if olay not in GECERLI_OLAYLAR:
        raise ValueError(f"Bilinmeyen hook olayı: {olay!r}. Geçerliler: {sorted(GECERLI_OLAYLAR)}")
    if olay not in _HOOK_KAYDI:
        _HOOK_KAYDI[olay] = []
    if callback not in _HOOK_KAYDI[olay]:
        _HOOK_KAYDI[olay].append(callback)
        log.debug("Hook kayıt: olay=%s callback=%s", olay, getattr(callback, "__name__", repr(callback)))


def hook_kaldir(olay: str, callback: Callable) -> bool:
    """Kayıtlı bir hook'u kaldır. Başarıyla kaldırıldıysa True döner."""
    if olay in _HOOK_KAYDI and callback in _HOOK_KAYDI[olay]:
        _HOOK_KAYDI[olay].remove(callback)
        return True
    return False


def hook_cagir(olay: str, **kwargs: Any) -> List[Any]:
    """Bir olayın tüm kayıtlı hook'larını ateşle.

    Her hook ayrı try/except ile korunur — biri çökmesi diğerlerini
    durdurmaz. Hata durumunda log.warning yazar ve devam eder.

    Args:
        olay:    Hook olay adı.
        **kwargs: Hook'a iletilecek named argümanlar.

    Returns:
        Hook return değerlerinin listesi (None'lar dahil).
    """
    callback_ler = _HOOK_KAYDI.get(olay, [])
    if not callback_ler:
        return []

    sonuclar: List[Any] = []
    for cb in callback_ler:
        t0 = time.monotonic()
        try:
            sonuc = cb(**kwargs)
            sonuclar.append(sonuc)
        except Exception as e:
            gecen = time.monotonic() - t0
            log.warning(
                "Hook başarısız: olay=%s callback=%s sure=%.3fs hata=%s",
                olay,
                getattr(cb, "__name__", repr(cb)),
                gecen,
                e,
            )
            sonuclar.append(None)
    return sonuclar


# ── Sık kullanılan olay ateşleyicileri ──────────────────────────────────────

def oturum_baslat_tetikle(session_id: str, agent_adi: str = "", **kw) -> None:
    hook_cagir("on_session_start", session_id=session_id, agent_adi=agent_adi, **kw)


def oturum_bitir_tetikle(session_id: str, tur_sayisi: int = 0, **kw) -> None:
    hook_cagir("on_session_end", session_id=session_id, tur_sayisi=tur_sayisi, **kw)


def tur_baslat_tetikle(tur: int, task_id: str = "", **kw) -> None:
    hook_cagir("on_turn_start", tur=tur, task_id=task_id, **kw)


def tur_bitir_tetikle(tur: int, basarili: bool = True, **kw) -> None:
    hook_cagir("on_turn_end", tur=tur, basarili=basarili, **kw)


def arac_cagri_tetikle(arac_adi: str, argumanlar: dict, **kw) -> None:
    hook_cagir("on_tool_call", arac_adi=arac_adi, argumanlar=argumanlar, **kw)


def arac_sonuc_tetikle(arac_adi: str, sonuc: str, sure_sn: float = 0.0, **kw) -> None:
    hook_cagir("on_tool_result", arac_adi=arac_adi, sonuc=sonuc, sure_sn=sure_sn, **kw)


def hata_tetikle(hata: Exception, olay_baglami: str = "", **kw) -> None:
    hook_cagir("on_error", hata=hata, olay_baglami=olay_baglami, **kw)


def context_sikistirma_tetikle(mesaj_sayisi: int, token_tahmini: int = 0, **kw) -> None:
    hook_cagir("on_context_compress", mesaj_sayisi=mesaj_sayisi, token_tahmini=token_tahmini, **kw)


# ── ReYMeN uyumluluğu için alias ─────────────────────────────────────────────
invoke_hook = hook_cagir
register_hook = hook_kaydet


def tum_hooklari_temizle() -> None:
    """Tüm kayıtlı hook'ları temizle (test izolasyonu için)."""
    _HOOK_KAYDI.clear()


def kayitli_hooklar() -> Dict[str, List[str]]:
    """Kayıtlı hook'ların okunabilir özetini döndür."""
    return {
        olay: [getattr(cb, "__name__", repr(cb)) for cb in cblar]
        for olay, cblar in _HOOK_KAYDI.items()
        if cblar
    }


# ── Decorator tabanlı kayıt ──────────────────────────────────────────────────

def hook(olay: str) -> Callable:
    """Hook kaydı için decorator.

    Örnek::

        @hook("on_session_start")
        def oturum_basladi(session_id: str, **kwargs):
            log.info(f"Oturum başladı: {session_id}")
    """
    def _decorator(fn: Callable) -> Callable:
        hook_kaydet(olay, fn)
        return fn
    return _decorator


# ═══════════════════════════════════════════════════════════════════════════════
# HookDispatcher class — Thread-safe olay dağıtıcı (eski sistem/hook_dispatcher)
# ═══════════════════════════════════════════════════════════════════════════════

from collections import defaultdict as _defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

_hd_logger = logging.getLogger("HookDispatcher")


class HookDispatcher:
    """Olay dagitici.

    Uygulama icindeki olaylari (hook'lari) dinler ve
    kayitli callback fonksiyonlarini tetikler.
    """

    def __init__(self, max_workers=4):
        """HookDispatcher baslatma.

        Args:
            max_workers: Ayni anda calisacak maksimum is parcacigi
        """
        self._hooks = _defaultdict(list)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._aktif = True
        self._istatistik = _defaultdict(int)

    def kaydet(self, olay, fn):
        """Bir olay icin callback fonksiyonu kaydet.

        Args:
            olay: Olay adi (ornek: "TOOL_CALLED", "TOOL_ERROR")
            fn: Callback fonksiyonu

        Returns:
            Basarili mesaj veya hata mesaji
        """
        try:
            if not callable(fn):
                return "[HookDispatcher] fn cagrilabilir olmali."

            if fn not in self._hooks[olay]:
                self._hooks[olay].append(fn)
                _hd_logger.info(f"Hook kaydedildi: {olay} -> {fn.__name__}")
                return f"[HookDispatcher] '{olay}' icin {fn.__name__} kaydedildi."
            else:
                return f"[HookDispatcher] {fn.__name__} zaten kayitli."

        except Exception as e:
            _hd_logger.exception("Hook kayit hatasi")
            return f"[HookDispatcher] Kayit hatasi: {e}"

    def kaldir(self, olay, fn):
        """Bir olay icin kayitli callback fonksiyonunu kaldir.

        Args:
            olay: Olay adi
            fn: Kaldirilacak callback fonksiyonu

        Returns:
            Basarili mesaj veya hata mesaji
        """
        try:
            if olay not in self._hooks:
                return f"[HookDispatcher] '{olay}' icin hook bulunamadi."

            if fn in self._hooks[olay]:
                self._hooks[olay].remove(fn)
                _hd_logger.info(f"Hook kaldirildi: {olay} -> {fn.__name__}")
                return f"[HookDispatcher] '{olay}' icin {fn.__name__} kaldirildi."
            else:
                return f"[HookDispatcher] {fn.__name__} bu olayda kayitli degil."

        except Exception as e:
            _hd_logger.exception("Hook kaldirma hatasi")
            return f"[HookDispatcher] Kaldirma hatasi: {e}"

    def tetikle(self, olay, **data):
        """Bir olayi tetikle ve kayitli tum callback'leri calistir.

        Args:
            olay: Tetiklenecek olay adi
            **data: Callback'lere gonderilecek veri

        Returns:
            Sonuc metni veya hata mesaji
        """
        try:
            if not self._aktif:
                return "[HookDispatcher] Dagitic kapali."

            if olay not in self._hooks or not self._hooks[olay]:
                return f"[HookDispatcher] '{olay}' icin hook yok."

            fonsiyonlar = self._hooks[olay]
            self._istatistik[olay] += 1
            basarili = 0
            basarisiz = 0

            # Callback'leri paralel calistir
            futures = {}
            for fn in fonsiyonlar:
                try:
                    future = self._executor.submit(self._guvenli_calistir, fn, olay, data)
                    futures[future] = fn
                except Exception as e:
                    _hd_logger.error(f"{fn.__name__} baslatilamadi: {e}")
                    basarisiz += 1

            # Sonuclari topla
            for future in as_completed(futures, timeout=30):
                fn = futures[future]
                try:
                    sonuc = future.result(timeout=5)
                    if sonuc:
                        basarili += 1
                    else:
                        basarisiz += 1
                except Exception as e:
                    _hd_logger.error(f"{fn.__name__} sonuc hatasi: {e}")
                    basarisiz += 1

            return (
                f"[HookDispatcher] '{olay}' tetiklendi: "
                f"{basarili} basarili, {basarisiz} basarisiz"
            )

        except Exception as e:
            _hd_logger.exception("Tetikleme hatasi")
            return f"[HookDispatcher] Tetikleme hatasi: {e}"

    def _guvenli_calistir(self, fn, olay, data):
        """Bir callback'i try/except ile guvenli calistir.

        Args:
            fn: Callback fonksiyonu
            olay: Olay adi
            data: Veri sozlugu

        Returns:
            True basarili, False basarisiz
        """
        try:
            fn(olay=olay, **data)
            return True
        except Exception as e:
            _hd_logger.error(
                f"Hook hatasi [{olay}/{fn.__name__}]: {e}"
            )
            return False

    def listele(self, olay=None):
        """Kayitli hook'lari listele.

        Args:
            olay: Filtre olay adi (opsiyonel)

        Returns:
            Hook listesi metni
        """
        try:
            if olay:
                if olay not in self._hooks:
                    return f"[HookDispatcher] '{olay}' icin hook yok."
                olaylar = {olay: self._hooks[olay]}
            else:
                olaylar = dict(self._hooks)

            if not olaylar:
                return "[HookDispatcher] Kayitli hook yok."

            liste = []
            for o, fns in sorted(olaylar.items()):
                fn_isimleri = [fn.__name__ for fn in fns]
                istatistik = self._istatistik.get(o, 0)
                liste.append(
                    f"  {o} ({istatistik} tetikleme): {', '.join(fn_isimleri)}"
                )

            return "[HookDispatcher] Kayitli hooklar:\\n" + "\\n".join(liste)

        except Exception as e:
            _hd_logger.exception("Listeleme hatasi")
            return f"[HookDispatcher] Listeleme hatasi: {e}"

    def temizle(self, olay=None):
        """Hook'lari temizle.

        Args:
            olay: Belirli bir olayi temizle (None ise tumu)

        Returns:
            Basarili mesaj
        """
        try:
            if olay:
                adet = len(self._hooks.get(olay, []))
                self._hooks[olay] = []
                return f"[HookDispatcher] '{olay}' icin {adet} hook temizlendi."
            else:
                toplam = sum(len(v) for v in self._hooks.values())
                self._hooks.clear()
                return f"[HookDispatcher] {toplam} hook temizlendi."
        except Exception as e:
            return f"[HookDispatcher] Temizleme hatasi: {e}"

    def kapat(self):
        """Dagiticini kapat ve kaynaklari temizle.

        Returns:
            Basarili mesaj
        """
        try:
            self._aktif = False
            self._executor.shutdown(wait=False)
            return "[HookDispatcher] Dagitic kapatildi."
        except Exception as e:
            return f"[HookDispatcher] Kapatma hatasi: {e}"


def run(**kwargs):
    """HookDispatcher uzerinden islem yap.

    Args:
        islem: "kaydet", "kaldir", "tetikle", "listele"
        olay: Olay adi
        fn: Callback fonksiyonu (kaydet/kaldir icin)
        data: Tetikleme verisi (tetikle icin)

    Returns:
        Islem sonucu metni
    """
    try:
        dispatcher = HookDispatcher()
        islem = kwargs.get("islem", "listele")

        if islem == "kaydet":
            return dispatcher.kaydet(
                kwargs.get("olay", ""),
                kwargs.get("fn", None),
            )
        elif islem == "kaldir":
            return dispatcher.kaldir(
                kwargs.get("olay", ""),
                kwargs.get("fn", None),
            )
        elif islem == "tetikle":
            return dispatcher.tetikle(
                kwargs.get("olay", ""),
                **kwargs.get("data", {}),
            )
        else:
            return dispatcher.listele()

    except Exception as e:
        _hd_logger.exception("run hatasi")
        return f"[HookDispatcher] run hatasi: {e}"


if __name__ == "__main__":
    def ornek_hook(olay=None, **data):
        print(f"Hook calisti: {olay}, data={data}")

    d = HookDispatcher()
    d.kaydet("TEST", ornek_hook)
    print(d.listele())
    print(d.tetikle("TEST", mesaj="merhaba"))
