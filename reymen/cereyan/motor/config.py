"""motor/config.py — Sabitler, regex pattern'lar, konfigürasyon."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
_GATEWAY_STATE_PATH = ROOT / "gateway_state.json"
_TERCIH_DOSYASI = ROOT.parent / "setup.json"

RE_EYLEM = re.compile(r'Eylem:\s*([A-Z_]+)\s*\(((?:[^()]*|\([^()]*\))*)\)', re.DOTALL | re.IGNORECASE)
RE_ARAC_CAGRI = re.compile(r'([A-Z][A-Z_0-9]+)\s*\(((?:[^()]*|\([^()]*\))*)\)\s*$')
RE_ARAC_CAGRI_COK = re.compile(r'([A-Z][A-Z_0-9]+)\s*\(')
RE_PARAM = re.compile(r'"((?:[^"\\]|\\.)*)"')

BILINEN_ARACLAR = frozenset({
    "GOREV_BITTI", "DOSYA_OKU", "DOSYA_YAZ", "KOMUT_CALISTIR",
    "PYTHON_CALISTIR", "WEB_ARA", "TARAYICI_AC", "IC_GOZLEM",
    "HAFIZA_ARA", "PARALLEL_CALISTIR", "SKILL_ARA", "SKILL_AKTIVAT",
    "SKILL_KATEGORILER", "SKILL_SCRIPT", "ARAC_URET", "GUVENLI_CALISTIR",
})

RISKLI_ARACLAR = frozenset({
    "KOMUT_CALISTIR", "PYTHON_CALISTIR", "TARAYICI_AC",
    "EKRAN_TIKLA", "MAKRO_OYNAT", "ARAC_URET", "CUA_EKRAN_KULLAN",
})

TOOLSET_GRUPLARI = {
    "temel":    {"KOMUT_CALISTIR", "PYTHON_CALISTIR", "DOSYA_YAZ", "DOSYA_OKU",
                 "HAFIZA_ARA", "IC_GOZLEM", "PARALLEL_CALISTIR", "GOREV_BITTI"},
    "web":      {"WEB_ARA", "TARAYICI_AC"},
    "iletisim": {"TELEGRAM_GONDER", "TELEGRAM_RESIM_GONDER",
                 "TELEGRAM_STREAM_GONDER", "TELEGRAM_REACTION_EKLE", "TELEGRAM_PING"},
    "ekran":    {"EKRAN_OKU", "EKRAN_NISAN", "EKRAN_TIKLA", "MAKRO_OYNAT",
                 "UYG_ISLEM_CAGIR", "EKRAN_FOTOGRAF_CEK"},
    "dosya":    {"PDF_OKU", "EXCEL_OKU", "CSV_OKU", "GORUNTU_ANALIZ", "DOSYA_ANALIZ", "PROJE_TARA"},
    "skill":    {"SKILL_ARA", "SKILL_AKTIVAT", "SKILL_KATEGORILER", "SKILL_KATEGORI",
                 "SKILL_SCRIPT", "SKILL_OLUSTUR", "SKILL_DOGRULA", "SKILL_INDEX_YENILE",
                 "SKILL_SCRIPT_YARDIM", "SKILL_EVAL_EKLE", "SKILL_EVAL_LISTELE",
                 "ACHIEVEMENTS_LISTE"},
    "faz6":     {"ARAC_URET", "GUVENLI_CALISTIR"},
    "claude":   {"CLAUDE_YARDIM", "CLAUDE_ANALIZ", "CLAUDE_KOD_YAZ",
                 "CLAUDE_HATA_AYIKLA", "CLAUDE_PLAN", "CLAUDE_REVIZE", "CLAUDE_DURUM"},
    "gorev":    {"TODO", "CLARIFY", "EXECUTE_CODE", "TUI_BASLAT", "KANBAN_GUNCELLE", "KANBAN_OZET"},
    "hata":     {"HATA_WATCH_BASLAT", "HATA_WATCH_DURDUR", "HATA_KOD_AL",
                 "TERMINAL_HATA_PARSE", "COZUM_UYGULA"},
    "tor":      {"TOR_AC", "TOR_KAPAT", "TOR_FORM_DOLDUR", "TOR_LOGIN", "TOR_KAYIT", "TOR_SIPARIS"},
    "kopru":    {"KOPRU_BASLAT", "KOPRU_DURDUR", "KOPRU_DURUM"},
    "watchdog": {"WATCHDOG_KONTROL"},
}

DURUM_MESAJLARI = {
    "WEB_ARA": "İnternette aranıyor...", "TARAYICI_AC": "Sayfa açılıyor...",
    "DOSYA_OKU": "Dosya okunuyor...", "DOSYA_YAZ": "Dosya yazılıyor...",
    "KOMUT_CALISTIR": "Komut çalıştırılıyor...", "PYTHON_CALISTIR": "Python kodu çalıştırılıyor...",
    "HAFIZA_ARA": "Hafızada aranıyor...", "EKRAN_OKU": "Ekran okunuyor (OCR)...",
    "EKRAN_TIKLA": "Ekran öğesine tıklanıyor...", "TELEGRAM_GONDER": "Mesaj gönderiliyor...",
    "TELEGRAM_PING": "Telegram baglantisi test ediliyor...",
    "TELEGRAM_STREAM_GONDER": "Stream mesaj gonderiliyor...",
    "TELEGRAM_REACTION_EKLE": "Reaction ekleniyor...",
    "TELEGRAM_RESIM_GONDER": "Resim gönderiliyor...",
    "EKRAN_FOTOGRAF_CEK": "Ekran fotoğrafı çekiliyor...",
    "PARALLEL_CALISTIR": "Araçlar paralel çalıştırılıyor...",
    "PDF_OKU": "PDF okunuyor...", "EXCEL_OKU": "Excel dosyası okunuyor...",
    "CSV_OKU": "CSV dosyası okunuyor...", "GORUNTU_ANALIZ": "Görüntü analiz ediliyor (LLaVA)...",
    "DOSYA_ANALIZ": "Dosya analiz ediliyor...", "PROJE_TARA": "Proje dosyalari taranıyor...",
    "SKILL_AKTIVAT": "Skill yukleniyor...", "SKILL_KATEGORI": "Skill kategorisi listeleniyor...",
    "SKILL_SCRIPT": "Skill scripti calistiriliyor...", "SKILL_OLUSTUR": "Yeni skill olusturuluyor...",
    "SKILL_DOGRULA": "Skill dogrulanıyor (spec kontrol)...",
    "SKILL_INDEX_YENILE": "Skill FTS5 indexi yenileniyor...",
    "SKILL_SCRIPT_YARDIM": "Script arayuzu ogreniyor (--help)...",
    "SKILL_EVAL_EKLE": "Skill eval test case ekleniyor...",
    "SKILL_EVAL_LISTELE": "Skill eval listesi getiriliyor...",
    "ARAC_URET": "Yeni arac uretiliyor (Code-As-A-Tool)...",
    "GUVENLI_CALISTIR": "Guvenli sandbox'ta kod calistiriliyor...",
    "HATA_WATCH_BASLAT": "Hata watchdog baslatiliyor (ekran izleme)...",
    "HATA_WATCH_DURDUR": "Hata watchdog durduruluyor...",
    "HATA_KOD_AL": "Hata kodu aliniyor...",
    "TERMINAL_HATA_PARSE": "Terminal ciktisi hata icin taranıyor...",
    "COZUM_UYGULA": "Cozum uygulaniyor (patch)...",
    "TOR_AC": "Tor Browser baslatiliyor...", "TOR_KAPAT": "Tor Browser kapatiliyor...",
    "TOR_FORM_DOLDUR": "Form dolduruluyor...", "TOR_LOGIN": "Siteye giris yapiliyor...",
    "TOR_KAYIT": "Yeni kayit olusturuluyor...", "TOR_SIPARIS": "Siparis veriliyor...",
    "CUA_EKRAN_KULLAN": "CUA: Ekran vizyon+koordinat+eylem...",
    "CUA_ARACLARI_TARA": "CUA bilesenleri taranıyor...",
    "ACHIEVEMENTS_LISTE": "Rozetler listeleniyor...", "PROXY_AYARLA": "Proxy yapilandiriliyor...",
    "CLARIFY": "Talep netleştiriliyor...", "EXECUTE_CODE": "Python kodu çalıştırılıyor...",
    "TUI_BASLAT": "Terminal UI baslatiliyor...",
    "KOPRU_BASLAT": "Telegram Bridge baslatiliyor (Bot1/Bot2)...",
    "KOPRU_DURDUR": "Telegram Bridge durduruluyor...",
    "KOPRU_DURUM": "Telegram Bridge durumu sorgulaniyor...",
}

CORE_TOOLS = [
    "web_search", "terminal", "file_read", "file_write", "file_edit",
    "memory", "session_search", "skill_view", "skills_list",
    "process", "todo", "clarify", "cronjob", "patch",
    "search_files", "skill_manage", "x_search",
]

OPTIONAL_TOOLS = {
    "browser": ["web_extract", "browser_navigate", "browser_click", "browser_type",
                "browser_scroll", "browser_press", "browser_snapshot",
                "browser_get_images", "browser_vision", "browser_console",
                "browser_cdp", "browser_dialog"],
    "vision": ["vision_analyze", "image_generate"],
    "code": ["execute_code", "delegate_task"],
    "media": ["text_to_speech", "audio_transcribe"],
    "powerbi": ["powerbi_connect", "powerbi_query", "powerbi_tables", "powerbi_measures"],
    "video": ["video_analyze", "video_transcript", "video_info"],
    "automation": ["n8n_trigger", "n8n_status", "n8n_list"],
    "swarm": ["swarm_run", "swarm_pipeline", "swarm_demo"],
    "kanban": ["kanban_show", "kanban_list", "kanban_complete", "kanban_block"],
    "homeassistant": ["ha_list_entities", "ha_get_state"],
}

VARSAYILAN_MODELLER = {
    "deepseek": "deepseek-v4-flash", "xiaomi": "mimo-v2.5-pro",
    "groq": "deepseek-v4-flash", "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4", "openrouter": "openai/gpt-4o",
    "xai": "grok-3", "lmstudio": "local-model", "ollama": "llama3",
}

PROVIDER_ENV = {
    "deepseek": "DEEPSEEK_API_KEY", "xiaomi": "XIAOMI_API_KEY",
    "groq": "GROQ_API_KEY", "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY", "openrouter": "OPENROUTER_API_KEY",
    "xai": "XAI_API_KEY", "lmstudio": "", "ollama": "",
}

PROVIDER_URL = {
    "deepseek": "https://api.deepseek.com", "xiaomi": "https://api.xiaomimimo.com",
    "groq": "https://api.groq.com/openai/v1", "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com", "openrouter": "https://openrouter.ai/api/v1",
    "xai": "https://api.x.ai/v1", "lmstudio": "http://localhost:1234/v1",
    "ollama": "http://localhost:11434/v1",
}

PROVIDER_TEST_MAP = {
    "deepseek": ("DEEPSEEK_API_KEY", "https://api.deepseek.com/v1/chat/completions", "deepseek-v4-flash"),
    "xiaomi": ("XIAOMI_API_KEY", "https://api.xiaomimimo.com/v1/chat/completions", "mimo-v2.5-pro"),
    "groq": ("GROQ_API_KEY", "https://api.groq.com/openai/v1/chat/completions", "deepseek-v4-flash"),
    "openai": ("OPENAI_API_KEY", "https://api.openai.com/v1/chat/completions", "gpt-4o"),
    "anthropic": ("ANTHROPIC_API_KEY", "https://api.anthropic.com/v1/messages", "claude-sonnet-4"),
    "openrouter": ("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1/chat/completions", "openai/gpt-4o"),
    "xai": ("XAI_API_KEY", "https://api.x.ai/v1/chat/completions", "grok-3"),
    "lmstudio": ("", "http://localhost:1234/v1/chat/completions", "local-model"),
    "ollama": ("", "http://localhost:11434/v1/chat/completions", "llama3"),
}

GECERLI_PROVIDERLER = list(VARSAYILAN_MODELLER.keys())
MAX_PARALLEL_WORKERS = 8
PARALLEL_TIMEOUT_VARSAYILAN = 30


def get_active_tools(context=None):
    """Aktif tool'ları döndür — context'e göre filtrele."""
    tools = list(CORE_TOOLS)
    if context:
        if context.get("web_needed"):
            tools.extend(OPTIONAL_TOOLS.get("browser", []))
        if context.get("vision_needed"):
            tools.extend(OPTIONAL_TOOLS.get("vision", []))
        if context.get("code_needed"):
            tools.extend(OPTIONAL_TOOLS.get("code", []))
        if context.get("powerbi_needed"):
            tools.extend(OPTIONAL_TOOLS.get("powerbi", []))
        if context.get("video_needed"):
            tools.extend(OPTIONAL_TOOLS.get("video", []))
        if context.get("automation_needed"):
            tools.extend(OPTIONAL_TOOLS.get("automation", []))
        if context.get("swarm_needed"):
            tools.extend(OPTIONAL_TOOLS.get("swarm", []))
        if context.get("kanban_needed"):
            tools.extend(OPTIONAL_TOOLS.get("kanban", []))
        if context.get("ha_needed"):
            tools.extend(OPTIONAL_TOOLS.get("homeassistant", []))
    return tools
