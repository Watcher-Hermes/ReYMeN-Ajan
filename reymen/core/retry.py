# -*- coding: utf-8 -*-
"""
retry — Genel amaçlı yeniden deneme (retry) mekanizması.

Destekler:
  - Sabit / üstel geri çekilme (fixed / exponential backoff)
  - Maksimum deneme sayısı ve zaman aşımı
  - Belirli exception türlerini yakalama / atlama
  - Decorator (class ve fonksiyon için)
  - Senkron çalışma (thread-safe değil, tek线程 için)

Kullanım:
    from reymen.core.retry import retry, RetryConfig

    @retry(max_attempts=3, delay=0.5, backoff=2.0)
    def riskli_islem():
        return risky_api_call()

    # Config ile:
    cfg = RetryConfig(max_attempts=5, delay=1.0, exceptions=(ConnectionError,))
    sonuc = cfg.execute(lambda: unstable_network_call())
"""

import time
import random
import functools
from typing import (
    Callable,
    Optional,
    Tuple,
    Type,
    Union,
    Any,
)


# ── Config ────────────────────────────────────────────────────────────────────


class RetryConfig:
    """Yeniden deneme yapılandırması.

    Args:
        max_attempts: Maksimum deneme sayısı (default: 3).
        delay: İlk bekleme süresi saniye (default: 1.0).
        max_delay: Maksimum bekleme süresi (default: 60.0).
        backoff: Üstel geri çekilme çarpanı (default: 2.0).
        jitter: Rastgele gecikme payı oranı (default: 0.1, 0 = jitter yok).
        exceptions: Yakalanacak exception türleri (default: Exception).
        ignore_exceptions: Atlanacak exception türleri (default: ()).
        timeout: Toplam zaman aşımı saniye (default: 0 = limitsiz).
    """

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        max_delay: float = 60.0,
        backoff: float = 2.0,
        jitter: float = 0.1,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        ignore_exceptions: Tuple[Type[Exception], ...] = (),
        timeout: float = 0.0,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts en az 1 olmalı")
        if delay < 0:
            raise ValueError("delay negatif olamaz")
        if backoff < 1.0:
            raise ValueError("backoff en az 1.0 olmalı")
        if jitter < 0 or jitter > 1:
            raise ValueError("jitter 0-1 arasında olmalı")

        self.max_attempts = max_attempts
        self.delay = delay
        self.max_delay = max_delay
        self.backoff = backoff
        self.jitter = jitter
        self.exceptions = exceptions
        self.ignore_exceptions = ignore_exceptions
        self.timeout = timeout

    # ── Execute ────────────────────────────────────────────────────────────────

    def execute(self, fn: Callable, *args, **kwargs) -> Any:
        """Fonksiyonu yeniden deneme mantığıyla çalıştır.

        Args:
            fn: Çağrılacak fonksiyon.
            *args, **kwargs: Fonksiyona iletilecek argümanlar.

        Returns:
            Fonksiyonun başarılı sonucu.

        Raises:
            Son denemede oluşan exception (yakalanabilir türlerden).
        """
        baslangic = time.monotonic()
        son_hata: Optional[Exception] = None

        for deneme in range(1, self.max_attempts + 1):
            try:
                return fn(*args, **kwargs)
            except self.ignore_exceptions:
                raise  # atlanacak tür -> hiç yakalama
            except self.exceptions as e:
                son_hata = e
                if deneme == self.max_attempts:
                    break

                # Zaman aşımı kontrolü
                if self.timeout > 0 and (time.monotonic() - baslangic) >= self.timeout:
                    break

                # Bekleme süresini hesapla
                bekle = self._bekleme_suresi(deneme)
                time.sleep(bekle)
            except BaseException:
                raise  # SystemExit/KBInterrupt vb. hiç yakalanmasın

        if son_hata is not None:
            raise son_hata  # type: ignore[misc]

        return None  # bu noktaya gelinmez

    # ── Yardımcılar ───────────────────────────────────────────────────────────

    def _bekleme_suresi(self, deneme: int) -> float:
        """Üstel geri çekilme + jitter ile bekleme süresi hesapla."""
        sure = self.delay * (self.backoff ** (deneme - 1))
        sure = min(sure, self.max_delay)
        if self.jitter > 0:
            sure += random.uniform(-sure * self.jitter, sure * self.jitter)
            sure = max(0.0, sure)
        return sure

    def __repr__(self) -> str:
        return (
            f"RetryConfig(max={self.max_attempts}, "
            f"delay={self.delay}, backoff={self.backoff})"
        )

    def __str__(self) -> str:
        return (
            f"Retry(max={self.max_attempts} delay={self.delay}s "
            f"backoff={self.backoff}x jitter={self.jitter})"
        )


# ── Decorator ──────────────────────────────────────────────────────────────────


# Global config havuzu (decorator ile kullanılan)
_CONFIG_HATIRLA: dict[str, RetryConfig] = {}


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    max_delay: float = 60.0,
    jitter: float = 0.1,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ignore_exceptions: Tuple[Type[Exception], ...] = (),
    timeout: float = 0.0,
    config: Optional[RetryConfig] = None,
):
    """Decorator: fonksiyonu yeniden deneme mantığıyla sar.

    Args:
        config: Hazır RetryConfig nesnesi (varsa diğer parametreler yok sayılır).
        Diğer parametreler RetryConfig ile aynı.

    Kullanım:
        @retry(max_attempts=3, delay=0.5)
        def veri_cek(url):
            ...

        @retry(config=RetryConfig(max_attempts=5, delay=2.0))
        def agir_islem():
            ...
    """
    cfg = config or RetryConfig(
        max_attempts=max_attempts,
        delay=delay,
        max_delay=max_delay,
        backoff=backoff,
        jitter=jitter,
        exceptions=exceptions,
        ignore_exceptions=ignore_exceptions,
        timeout=timeout,
    )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return cfg.execute(func, *args, **kwargs)

        # Debug / introspection için
        wrapper.retry_config = cfg  # type: ignore[attr-defined]
        wrapper.retry_sifirla = lambda: None  # type: ignore[attr-defined]

        return wrapper

    return decorator


# ── Kolaylık fonksiyonları ────────────────────────────────────────────────────


def geri_cek(
    fn: Callable,
    *args,
    max_attempts: int = 3,
    delay: float = 1.0,
    **kwargs,
) -> Any:
    """Tek çağrıda retry ile çalıştır (decorator'suz).

    Args:
        fn: Çağrılacak fonksiyon.
        *args: Fonksiyon argümanları.
        max_attempts: Maksimum deneme sayısı.
        delay: İlk bekleme süresi.
        **kwargs: RetryConfig ve fn için ek argümanlar.

    Returns:
        Başarılı sonuç.
    """
    cfg_keys = {"backoff", "max_delay", "jitter", "exceptions",
                 "ignore_exceptions", "timeout"}
    cfg_kw = {k: kwargs.pop(k) for k in list(kwargs.keys())
              if k in cfg_keys}
    cfg = RetryConfig(max_attempts=max_attempts, delay=delay, **cfg_kw)
    return cfg.execute(fn, *args, **kwargs)
