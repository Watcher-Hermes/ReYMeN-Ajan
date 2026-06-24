# -*- coding: utf-8 -*-
"""Bellek yöneticisi — memory provider'ları orkestra eder.

Adapted from Hermes Agent (MIT License, Nous Research)
https://github.com/NousResearch/hermes-agent

MemoryManager, dahili ve harici bellek sağlayıcılarını (providers)
tek bir merkezi noktadan yönetir. Tek bir harici sağlayıcıya izin verir.

Kullanım:
    from reymen.sistem.memory_manager import MemoryManager

    mm = MemoryManager(config)
    mm.add_provider(my_provider)
    prompt = mm.build_system_prompt()
    context = mm.prefetch_all(user_message)
    mm.sync_all(user_msg, assistant_response)
"""

from __future__ import annotations

import inspect
import json
import logging
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Arka plan senkronizasyonu için azami bekleme süresi (saniye)
_SYNC_DRAIN_TIMEOUT_S = 5.0


# ═══════════════════════════════════════════════════════════════════════════════
# Soyut MemoryProvider Arayüzü
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryProvider:
    """MemoryProvider soyut temel sınıfı.

    Her bellek sağlayıcısı bu sınıfı genişletmeli ve aşağıdaki
    metodları uygulamalıdır.
    """

    @property
    def name(self) -> str:
        """Sağlayıcı adı."""
        return "abstract"

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Araç şemalarını döner."""
        return []

    def system_prompt_block(self) -> str:
        """System prompt'a eklenecek bloğu döner."""
        return ""

    def prefetch(self, query: str, *, session_id: str = "") -> Optional[str]:
        """Verilen sorgu için önceden bellek bağlamı toplar."""
        return None

    def queue_prefetch(self, query: str, *, session_id: str = "") -> None:
        """Sonraki tur için arka plan prefetch kuyruğu oluşturur."""
        pass

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Tamamlanmış bir turu sağlayıcıya senkronize eder."""
        pass

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs) -> str:
        """Araç çağrısını işler, JSON string sonuç döner."""
        return '{"error": "not implemented"}'

    def on_turn_start(self, turn_number: int, message: str, **kwargs) -> None:
        """Yeni bir turun başladığını bildirir."""
        pass

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        """Oturum sonlandığını bildirir."""
        pass

    def on_session_switch(
        self,
        new_session_id: str,
        *,
        parent_session_id: str = "",
        reset: bool = False,
        **kwargs,
    ) -> None:
        """Oturum kimliği değiştiğinde bildirir."""
        pass

    def on_pre_compress(self, messages: List[Dict[str, Any]]) -> str:
        """Bağlam sıkıştırmasından önce bildirir, özet metin döner."""
        return ""

    def on_memory_write(
        self, action: str, target: str, content: str, **kwargs
    ) -> None:
        """Dahili bellek yazımı gerçekleştiğinde bildirir."""
        pass

    def on_delegation(self, task: str, result: str, **kwargs) -> None:
        """Alt ajan tamamlandığında bildirir."""
        pass

    def initialize(self, session_id: str = "", **kwargs) -> None:
        """Sağlayıcıyı başlatır."""
        pass

    def shutdown(self) -> None:
        """Sağlayıcıyı kapatır."""
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# Bağlam Çitleri Yardımcıları
# ═══════════════════════════════════════════════════════════════════════════════

_FENCE_TAG_RE = re.compile(r'</?\s*memory-context\s*>', re.IGNORECASE)
_INTERNAL_CONTEXT_RE = re.compile(
    r'<\s*memory-context\s*>[\s\S]*?</\s*memory-context\s*>', re.IGNORECASE,
)
_INTERNAL_NOTE_RE = re.compile(
    r'\[System note:\s*The following is recalled memory context,'
    r'\s*NOT new user input\.\s*Treat as'
    r' (?:informational background data|authoritative reference data[^]]*)\.\]\s*',
    re.IGNORECASE,
)


def sanitize_context(text: str) -> str:
    """Sağlayıcı çıktısındaki fence tag'leri, enjekte edilmiş bağlam bloklarını
    ve system notlarını temizler."""
    text = _INTERNAL_CONTEXT_RE.sub('', text)
    text = _INTERNAL_NOTE_RE.sub('', text)
    text = _FENCE_TAG_RE.sub('', text)
    return text


class StreamingContextScrubber:
    """Streaming metin için durum tabanlı temizleyici.

    Tek atımlı ``sanitize_context`` regex'i chunk sınırlarında
    başarısız olur. Bu temizleyici delta'lar arası durum makinesi
    çalıştırır.

    Kullanım::

        scrubber = StreamingContextScrubber()
        for delta in stream:
            visible = scrubber.feed(delta)
            if visible:
                emit(visible)
        trailing = scrubber.flush()
        if trailing:
            emit(trailing)
    """

    _OPEN_TAG = "<memory-context>"
    _CLOSE_TAG = "</memory-context>"

    def __init__(self) -> None:
        self._in_span: bool = False
        self._buf: str = ""
        self._at_block_boundary: bool = True

    def reset(self) -> None:
        """Temizleyiciyi sıfırlar."""
        self._in_span = False
        self._buf = ""
        self._at_block_boundary = True

    def feed(self, text: str) -> str:
        """``text``'in görünür kısmını temizleyerek döner."""
        if not text:
            return ""
        buf = self._buf + text
        self._buf = ""
        out: list[str] = []

        while buf:
            if self._in_span:
                idx = buf.lower().find(self._CLOSE_TAG)
                if idx == -1:
                    held = self._max_partial_suffix(buf, self._CLOSE_TAG)
                    self._buf = buf[-held:] if held else ""
                    return "".join(out)
                buf = buf[idx + len(self._CLOSE_TAG):]
                self._in_span = False
            else:
                idx = buf.lower().find(self._OPEN_TAG)
                if idx == -1:
                    held = self._max_partial_suffix(buf, self._OPEN_TAG)
                    if held:
                        out.append(buf[:-held])
                        self._buf = buf[-held:]
                    else:
                        out.append(buf)
                    return "".join(out)
                if idx > 0:
                    out.append(buf[:idx])
                buf = buf[idx + len(self._OPEN_TAG):]
                self._in_span = True

        return "".join(out)

    def flush(self) -> str:
        """Stream sonunda tampon内的 tutulan içeriği temizler."""
        if self._in_span:
            self._buf = ""
            self._in_span = False
            return ""
        tail = self._buf
        self._buf = ""
        return tail

    @staticmethod
    def _max_partial_suffix(buf: str, tag: str) -> int:
        """Buf'un en uzun tag-prefix olan son ek uzunluğunu döner."""
        tag_lower = tag.lower()
        buf_lower = buf.lower()
        max_check = min(len(buf_lower), len(tag_lower) - 1)
        for i in range(max_check, 0, -1):
            if tag_lower.startswith(buf_lower[-i:]):
                return i
        return 0


def build_memory_context_block(raw_context: str) -> str:
    """Önceden getirilmiş bellek bağlamını fence'li blokla sarar."""
    if not raw_context or not raw_context.strip():
        return ""
    clean = sanitize_context(raw_context)
    if clean != raw_context:
        logger.warning("bellek sağlayıcısı önceden sarılmış bağlam döndürdü; temizlendi")
    return (
        "<memory-context>\n"
        "[System note: The following is recalled memory context, "
        "NOT new user input. Treat as authoritative reference data — "
        "this is the agent's persistent memory and should inform all responses.]\n\n"
        f"{clean}\n"
        "</memory-context>"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MemoryManager — Ana Orkestratör
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryManager:
    """Dahili ve en fazla bir harici memory provider'ını orkestra eder.

    Dahili provider her zaman önce gelir. Yalnızca bir harici
    (non-builtin) sağlayıcıya izin verilir. Bir sağlayıcıdaki
    hatalar diğerini bloklamaz.
    """

    def __init__(self, config: Any = None) -> None:
        cfg = config or {}
        mem_cfg = cfg.get("memory", {}) if isinstance(cfg, dict) else {}
        self._max_kayit: int = mem_cfg.get("max_records", 2000)
        self._aktif: bool = True
        self._providers: List[MemoryProvider] = []
        self._tool_to_provider: Dict[str, MemoryProvider] = {}
        self._has_external: bool = False
        self._sync_executor: Optional[ThreadPoolExecutor] = None
        self._sync_executor_lock = threading.Lock()

    def ping(self) -> bool:
        """Yöneticinin aktif olup olmadığını kontrol eder."""
        return self._aktif

    # -- Türkçe API --------------------------------------------------------

    def kaydet(self, anahtar: str, icerik: Any, tur: str = "task") -> str:
        """Belleğe bilgi kaydeder.

        Args:
            anahtar: Kayıt anahtarı
            icerik: Kayıt içeriği
            tur: Kayıt türü (task, vector, longterm)
        """
        if tur not in ("task", "vector", "longterm"):
            return f"[Hafiza] Bilinmeyen tür: {tur}"
        key = f"{tur}:{anahtar}"
        if not hasattr(self, '_hafiza'):
            self._hafiza: dict = {}
        self._hafiza[key] = icerik
        return f"[Hafiza] Kaydedildi: {anahtar} ({tur})"

    def ara(self, sorgu: str) -> list:
        """Bellekte arama yapar."""
        if not hasattr(self, '_hafiza'):
            return []
        return [(k, v) for k, v in self._hafiza.items()
                if sorgu in k or (isinstance(v, str) and sorgu in v)]

    def durum(self) -> dict:
        """Yönetici durumunu döner."""
        return {"aktif": self._aktif, "max_kayit": self._max_kayit}

    def komut_islem(self, komut: str) -> str:
        """Metin tabanlı komut işler."""
        komut = (komut or "").strip()
        if not komut or komut in ("durum", "status"):
            return (
                "ReYMeN Hafiza Yöneticisi\n"
                "Komutlar: kaydet <metin>, ara <sorgu>, istatistik, durum"
            )
        parcalar = komut.split(None, 1)
        eylem = parcalar[0].lower()
        arguman = parcalar[1] if len(parcalar) > 1 else ""
        if eylem == "kaydet":
            if not arguman:
                return "Kullanim: kaydet <metin>"
            return self.kaydet(f"komut_{id(arguman)}", arguman)
        if eylem == "ara":
            if not arguman:
                return "Kullanim: ara <sorgu>"
            return f"[Hafiza] Arama: {arguman} → {len(self.ara(arguman))} sonuç"
        if eylem == "istatistik":
            n = len(getattr(self, '_hafiza', {}))
            return f"Istatistik — Aktif: {self._aktif}, Kayıt: {n}/{self._max_kayit}"
        return f"Bilinmeyen komut: {eylem}"

    # -- Kayıt ------------------------------------------------------------

    def add_provider(self, provider: MemoryProvider) -> None:
        """Bir bellek sağlayıcısı kaydeder.

        ``"builtin"`` adlı dahili sağlayıcı her zaman kabul edilir.
        Yalnızca **bir** harici sağlayıcıya izin verilir — ikinci
        deneme uyarı ile reddedilir.
        """
        is_builtin = provider.name == "builtin"

        if not is_builtin:
            if self._has_external:
                existing = next(
                    (p.name for p in self._providers if p.name != "builtin"), "unknown"
                )
                logger.warning(
                    "Bellek sağlayıcısı '%s' reddedildi — '%s' zaten kayıtlı. "
                    "Aynı anda yalnızca bir harici bellek sağlayıcısına izin verilir.",
                    provider.name, existing,
                )
                return
            self._has_external = True

        self._providers.append(provider)

        for schema in provider.get_tool_schemas():
            tool_name = schema.get("name", "")
            if tool_name and tool_name not in self._tool_to_provider:
                self._tool_to_provider[tool_name] = provider
            elif tool_name in self._tool_to_provider:
                logger.warning(
                    "Bellek araç adı çakışması: '%s' zaten %s tarafından kayıtlı, %s yoksayılıyor",
                    tool_name,
                    self._tool_to_provider[tool_name].name,
                    provider.name,
                )

        logger.info(
            "Bellek sağlayıcısı '%s' kaydedildi (%d araç)",
            provider.name, len(provider.get_tool_schemas()),
        )

    @property
    def providers(self) -> List[MemoryProvider]:
        """Kayıtlı tüm sağlayıcılar (sırayla)."""
        return list(self._providers)

    def get_provider(self, name: str) -> Optional[MemoryProvider]:
        """İsme göre sağlayıcı döner, yoksa None."""
        for p in self._providers:
            if p.name == name:
                return p
        return None

    # -- System Prompt -----------------------------------------------------

    def build_system_prompt(self) -> str:
        """Tüm sağlayıcılardan system prompt bloklarını toplar.

        Boş olmayan her blok sağlayıcı adıyla etiketlenir.
        """
        blocks = []
        for provider in self._providers:
            try:
                block = provider.system_prompt_block()
                if block and block.strip():
                    blocks.append(block)
            except Exception as e:
                logger.warning(
                    "Bellek sağlayıcısı '%s' system_prompt_block() başarısız: %s",
                    provider.name, e,
                )
        return "\n\n".join(blocks)

    # -- Prefetch / Recall -------------------------------------------------

    @staticmethod
    def _strip_skill_scaffolding(text: str) -> Optional[str]:
        """Skill/bundle çağrısından gerçek kullanıcı talimatını çıkarır."""
        # Basit bir çözüm: skill scaffolding yoksa aynen döner
        if not text or not text.strip():
            return None
        return text

    def prefetch_all(self, query: str, *, session_id: str = "") -> str:
        """Tüm sağlayıcılardan prefetch bağlamını toplar.

        Boş sağlayıcılar atlanır. Bir sağlayıcıdaki hatalar
        diğerlerini bloklamaz.
        """
        clean_query = self._strip_skill_scaffolding(query)
        if not clean_query:
            return ""
        parts = []
        for provider in self._providers:
            try:
                result = provider.prefetch(clean_query, session_id=session_id)
                if result and result.strip():
                    parts.append(result)
            except Exception as e:
                logger.debug(
                    "Bellek sağlayıcısı '%s' prefetch başarısız (öldürücü değil): %s",
                    provider.name, e,
                )
        return "\n\n".join(parts)

    def queue_prefetch_all(self, query: str, *, session_id: str = "") -> None:
        """Sonraki tur için tüm sağlayıcılarda arka plan prefetch kuyruğu oluşturur."""
        providers = list(self._providers)
        if not providers:
            return

        clean_query = self._strip_skill_scaffolding(query)
        if not clean_query:
            return

        def _run() -> None:
            for provider in providers:
                try:
                    provider.queue_prefetch(clean_query, session_id=session_id)
                except Exception as e:
                    logger.debug(
                        "Bellek sağlayıcısı '%s' queue_prefetch başarısız (öldürücü değil): %s",
                        provider.name, e,
                    )

        self._submit_background(_run)

    # -- Sync --------------------------------------------------------------

    @staticmethod
    def _provider_sync_accepts_messages(provider: MemoryProvider) -> bool:
        """sync_turn'un messages anahtar kelimesi kabul edip etmediğini kontrol eder."""
        try:
            signature = inspect.signature(provider.sync_turn)
        except (TypeError, ValueError):
            return True
        params = list(signature.parameters.values())
        if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params):
            return True
        return "messages" in signature.parameters

    def sync_all(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Tamamlanmış bir turu tüm sağlayıcılara senkronize eder.

        Arka plan iş parçacığında çalışır, satır-içi yolunu
        bloklamaz. Provider'ların ``sync_turn``'u engelleyici
        ağ/daemon çağrısı yapabilir.
        """
        providers = list(self._providers)
        if not providers:
            return

        clean_user_content = self._strip_skill_scaffolding(user_content)
        if not clean_user_content:
            return
        user_content = clean_user_content

        def _run() -> None:
            for provider in providers:
                try:
                    if messages is not None and self._provider_sync_accepts_messages(provider):
                        provider.sync_turn(
                            user_content,
                            assistant_content,
                            session_id=session_id,
                            messages=messages,
                        )
                    else:
                        provider.sync_turn(
                            user_content,
                            assistant_content,
                            session_id=session_id,
                        )
                except Exception as e:
                    logger.warning(
                        "Bellek sağlayıcısı '%s' sync_turn başarısız: %s",
                        provider.name, e,
                    )

        self._submit_background(_run)

    # -- Arka Plan Gönderimi -----------------------------------------------

    def _submit_background(self, fn: Any) -> None:
        """``fn``'i arka plan iş parçacığında çalıştırır.

        Executor tembel olarak oluşturulur. Kullanılamıyorsa
        ``fn`` satır-içi olarak çalıştırılır — asenkron avantajı
        kaybolur ama iş kaybolmaz.
        """
        executor = self._get_sync_executor()
        if executor is None:
            try:
                fn()
            except Exception as e:
                logger.debug("Satır-içi bellek arka plan görevi başarısız: %s", e)
            return
        try:
            executor.submit(fn)
        except RuntimeError:
            try:
                fn()
            except Exception as e:
                logger.debug("Satır-içi bellek arka plan görevi başarısız: %s", e)

    def _get_sync_executor(self) -> Optional[ThreadPoolExecutor]:
        """Tembel olarak tek iş parçacıklı arka plan executor'ı oluşturur."""
        if self._sync_executor is not None:
            return self._sync_executor
        with self._sync_executor_lock:
            if self._sync_executor is None:
                try:
                    self._sync_executor = ThreadPoolExecutor(
                        max_workers=1,
                        thread_name_prefix="mem-sync",
                    )
                except Exception as e:
                    logger.warning("Bellek senkronizasyon executor'ı oluşturulamadı: %s", e)
                    return None
            return self._sync_executor

    def flush_pending(self, timeout: Optional[float] = None) -> bool:
        """Kuyruktaki sync/prefetch işlerinin drain olmasını bekler.

        True eğer engel ``timeout`` içinde tamamlandıysa (veya executor yoksa),
        False zaman aşımında.
        """
        executor = self._sync_executor
        if executor is None:
            return True
        try:
            fut = executor.submit(lambda: None)
        except RuntimeError:
            return True
        try:
            fut.result(timeout=timeout)
            return True
        except Exception:
            return False

    # -- Araçlar -----------------------------------------------------------

    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        """Tüm sağlayıcılardan araç şemalarını toplar."""
        schemas = []
        seen = set()
        for provider in self._providers:
            try:
                for schema in provider.get_tool_schemas():
                    name = schema.get("name", "")
                    if name and name not in seen:
                        schemas.append(schema)
                        seen.add(name)
            except Exception as e:
                logger.warning(
                    "Bellek sağlayıcısı '%s' get_tool_schemas() başarısız: %s",
                    provider.name, e,
                )
        return schemas

    def get_all_tool_names(self) -> set:
        """Tüm araç adlarının kümesini döner."""
        return set(self._tool_to_provider.keys())

    def has_tool(self, tool_name: str) -> bool:
        """Bu aracın herhangi bir sağlayıcı tarafından işlenip işlenmediğini kontrol eder."""
        return tool_name in self._tool_to_provider

    def handle_tool_call(
        self, tool_name: str, args: Dict[str, Any], **kwargs
    ) -> str:
        """Araç çağrısını ilgili sağlayıcıya yönlendirir.

        JSON string sonuç döner. Hiçbir sağlayıcı aracın sahibi değilse
        ValueError fırlatır.
        """
        provider = self._tool_to_provider.get(tool_name)
        if provider is None:
            return json.dumps({"error": f"Tool '{tool_name}' not handled by any memory provider"})
        try:
            return provider.handle_tool_call(tool_name, args, **kwargs)
        except Exception as e:
            logger.error(
                "Bellek sağlayıcısı '%s' handle_tool_call(%s) başarısız: %s",
                provider.name, tool_name, e,
            )
            return json.dumps({"error": f"Memory tool '{tool_name}' failed: {e}"})

    # -- Yaşam Döngüsü Hook'ları -------------------------------------------

    def on_turn_start(self, turn_number: int, message: str, **kwargs) -> None:
        """Tüm sağlayıcılara yeni turu bildirir."""
        for provider in self._providers:
            try:
                provider.on_turn_start(turn_number, message, **kwargs)
            except Exception as e:
                logger.debug(
                    "Bellek sağlayıcısı '%s' on_turn_start başarısız: %s",
                    provider.name, e,
                )

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        """Tüm sağlayıcılara oturum sonu bildirir."""
        for provider in self._providers:
            try:
                provider.on_session_end(messages)
            except Exception as e:
                logger.warning(
                    "Bellek sağlayıcısı '%s' on_session_end başarısız: %s",
                    provider.name, e,
                )

    def on_session_switch(
        self,
        new_session_id: str,
        *,
        parent_session_id: str = "",
        reset: bool = False,
        rewound: bool = False,
        **kwargs,
    ) -> None:
        """Tüm sağlayıcılara oturum kimliği değişikliğini bildirir."""
        if not new_session_id:
            return
        if rewound:
            kwargs["rewound"] = True
        for provider in self._providers:
            try:
                provider.on_session_switch(
                    new_session_id,
                    parent_session_id=parent_session_id,
                    reset=reset,
                    **kwargs,
                )
            except Exception as e:
                logger.debug(
                    "Bellek sağlayıcısı '%s' on_session_switch başarısız: %s",
                    provider.name, e,
                )

    def on_pre_compress(self, messages: List[Dict[str, Any]]) -> str:
        """Bağlam sıkıştırmasından önce tüm sağlayıcılara bildirir."""
        parts = []
        for provider in self._providers:
            try:
                result = provider.on_pre_compress(messages)
                if result and result.strip():
                    parts.append(result)
            except Exception as e:
                logger.debug(
                    "Bellek sağlayıcısı '%s' on_pre_compress başarısız: %s",
                    provider.name, e,
                )
        return "\n\n".join(parts)

    def on_memory_write(
        self,
        action: str,
        target: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Harici sağlayıcılara dahili bellek yazımını bildirir."""
        for provider in self._providers:
            if provider.name == "builtin":
                continue
            try:
                provider.on_memory_write(
                    action, target, content, metadata=dict(metadata or {})
                )
            except Exception as e:
                logger.debug(
                    "Bellek sağlayıcısı '%s' on_memory_write başarısız: %s",
                    provider.name, e,
                )

    def on_delegation(self, task: str, result: str, **kwargs) -> None:
        """Tüm sağlayıcılara alt ajan tamamlanmasını bildirir."""
        for provider in self._providers:
            try:
                provider.on_delegation(task, result, **kwargs)
            except Exception as e:
                logger.debug(
                    "Bellek sağlayıcısı '%s' on_delegation başarısız: %s",
                    provider.name, e,
                )

    def shutdown_all(self) -> None:
        """Tüm sağlayıcıları kapatır (tersten sırayla).

        Önce arka plan executor'unu drain eder, ardından
        sağlayıcıları kapatır.
        """
        self._drain_sync_executor()
        for provider in reversed(self._providers):
            try:
                provider.shutdown()
            except Exception as e:
                logger.warning(
                    "Bellek sağlayıcısı '%s' kapatma başarısız: %s",
                    provider.name, e,
                )

    def _drain_sync_executor(self) -> None:
        """Arka plan executor'unu kapatır, kısa bir drain bekleme süresi ile."""
        with self._sync_executor_lock:
            executor = self._sync_executor
            self._sync_executor = None
        if executor is None:
            return
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except TypeError:
            try:
                executor.shutdown(wait=False)
            except Exception as e:
                logger.debug("Bellek senkronizasyon executor kapatma başarısız: %s", e)
            return
        except Exception as e:
            logger.debug("Bellek senkronizasyon executor kapatma başarısız: %s", e)
            return
        drainer = threading.Thread(
            target=lambda: self._bounded_executor_wait(executor),
            daemon=True,
            name="mem-sync-drain",
        )
        drainer.start()
        drainer.join(timeout=_SYNC_DRAIN_TIMEOUT_S)

    @staticmethod
    def _bounded_executor_wait(executor: ThreadPoolExecutor) -> None:
        try:
            executor.shutdown(wait=True)
        except Exception as e:
            logger.debug("Bellek senkronizasyon drain bekleme başarısız: %s", e)

    def initialize_all(self, session_id: str, **kwargs) -> None:
        """Tüm sağlayıcıları başlatır."""
        for provider in self._providers:
            try:
                provider.initialize(session_id=session_id, **kwargs)
            except Exception as e:
                logger.warning(
                    "Bellek sağlayıcısı '%s' initialize başarısız: %s",
                    provider.name, e,
                )

    # -- İstatistikler -----------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Bellek yöneticisi istatistiklerini döner."""
        provider_stats = []
        for p in self._providers:
            provider_stats.append({
                "name": p.name,
                "tool_count": len(p.get_tool_schemas()),
            })
        return {
            "aktif": self._aktif,
            "max_kayit": self._max_kayit,
            "provider_sayisi": len(self._providers),
            "dis_saglayici": self._has_external,
            "toplam_arac": len(self._tool_to_provider),
            "saglayicilar": provider_stats,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton Fabrika
# ═══════════════════════════════════════════════════════════════════════════════

_MEMORY_MANAGER_SINGLETON: Optional[MemoryManager] = None


def memory_manager(config: Any = None) -> MemoryManager:
    """Singleton MemoryManager örneği döner."""
    global _MEMORY_MANAGER_SINGLETON
    if _MEMORY_MANAGER_SINGLETON is None:
        _MEMORY_MANAGER_SINGLETON = MemoryManager(config)
    return _MEMORY_MANAGER_SINGLETON
