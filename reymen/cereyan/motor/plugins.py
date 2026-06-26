"""motor/plugins.py — Plugin, skill ve hook yönetimi."""
import logging
from reymen.cereyan.motor.config import ROOT

log = logging.getLogger("motor")

try:
    from tool_registry import ToolRegistry as _ToolRegistry
    _REGISTRY = _ToolRegistry()
except ImportError:
    _REGISTRY = None

try:
    from plugin_manager import PluginManager as _PluginManager
    _PLUGIN_MGR = _PluginManager(str(ROOT / "plugins"))
except ImportError:
    _PLUGIN_MGR = None

try:
    from plugin_loader import PluginYukleyici as _PluginYukleyici
    _PLUGIN_YUKLEYICI = _PluginYukleyici(dizin=ROOT / "plugins")
except ImportError:
    _PLUGIN_YUKLEYICI = None

try:
    from cua_motor_araci import CUA_EKRAN_KULLAN, CUA_ARACLARI_TARA
    _CUA_MEVCUT = True
except ImportError:
    _CUA_MEVCUT = False
    CUA_EKRAN_KULLAN = None
    CUA_ARACLARI_TARA = None


def plugin_arac_kaydet(ad: str, fonk, aciklama: str = "") -> None:
    if _REGISTRY:
        _REGISTRY.kaydet(ad, fonk)


def lazy_module_listesi() -> list:
    return [
        "persistence", "message_sanitization",
        "x_search_tool", "homeassistant_tool", "feishu_doc_tool",
        "yuanbao_tools", "model_tools", "mcp_tool",
        "rate_limiter", "araclar_web", "araclar_gelismis",
        "tools.discord_tool", "tools.browser_camofox", "tools.threat_patterns",
        "tools.delegate_tool", "tools.kanban_tools", "tools.voice_mode",
        "tools.clarify_tool", "tools.blueprints",
        "tools.mixture_of_agents_tool", "tools.vision_tools",
        "tools.code_execution_tool", "tools.osv_check", "tools.todo_tool",
        "tools.skills_hub", "tools.skills_sync",
        "tools.feishu_doc_tool", "tools.feishu_drive_tool",
        "tools.homeassistant_tool", "tools.session_search_tool",
        "tools.approval", "tools.write_approval", "plugins.memory",
        "tools.env_passthrough", "tools.env_probe",
        "tools.file_operations", "tools.file_state", "tools.file_tools",
        "tools.fuzzy_match", "tools.interrupt",
        "tools.process_registry", "tools.registry",
        "tools.thread_context", "tools.credential_files",
        "tools.schema_sanitizer", "tools.skill_provenance",
        "tools.skill_usage", "tools.tool_backend_helpers",
        "tools.browser_dialog_tool", "tools.browser_supervisor",
        "tools.web_tools", "tools.cronjob_tools",
        "tools.debug_helpers", "tools.mcp_oauth",
        "tools.microsoft_graph_auth", "tools.microsoft_graph_client",
        "tools.tool_output_limits", "tools.tool_result_storage",
        "tools.memory_tool", "tools.skill_tool",
        "tools.tts_tool", "tools.web_search_tool",
        "tools.session_search_tool", "tools.execute_code_tool",
        "tools.delegate_task_tool", "tools.context_tool",
        "tools.memory_providers",
        "tools.clarify_tool", "tools.todo_tool",
        "tools.ansi_strip", "tools.binary_extensions",
        "tools.browser_camofox_state", "tools.browser_tool",
        "tools.clarify_gateway", "tools.fal_common",
        "tools.lazy_deps", "tools.openrouter_client",
        "tools.patch_parser", "tools.read_extract",
        "tools.read_terminal_tool", "tools.skills_tool",
        "tools.tool_search", "tools.website_policy", "tools.xai_http",
        "kanban_orchestrator", "context_references",
        "araclar_makro", "araclar_ses", "araclar_telegram",
        "mcp_oauth", "batch_engine", "security_engine",
        "yetenek_fabrikasi", "sistem_sinyalleri",
        "mcp_oauth_manager", "reymen_batch_runner", "models_dev",
        "reyment", "araclar_ekran", "araclar_tarayici",
        "skill_bundles", "skill_commands", "telegram_bot",
        "reymen.arac.web_extract_tool", "reymen.arac.vision_analyze_tool",
        "reymen.arac.image_generate_tool", "reymen.arac.todo_tool",
        "reymen.arac.process_tool", "reymen.arac.file_ops_tool",
        "reymen.arac.cron_tool", "reymen.arac.memory_batch_tool",
        "reymen.arac.profile_tool", "reymen.arac.approval_tool",
        "reymen.arac.multi_platform_tool", "reymen.arac.browser_mcp_tool",
        "reymen.arac.powershell_tool", "reymen.sistem.model_switcher",
        "reymen.arac.web_search_tool", "reymen.cereyan.auto_web_search",
        "tools.claude_code_tool", "kopru", "tools.lsp_tool",
        "cua_motor_araci", "tools.mcp_tool", "agent.personalities",
        "closed_learning_loop", "hafiza_genislet", "acp_server",
        "tools.checkpoint_manager", "reymen.hafiza.reymen_memory_provider",
    ]


def skill_araclari_kaydet(motor) -> None:
    try:
        from skill_utils import skill_ara, kategorileri_listele, skill_oku
        plugin_arac_kaydet("SKILL_ARA", lambda sorgu="": str(skill_ara(sorgu)), "Skill veritabanında ara")
        plugin_arac_kaydet("SKILL_KATEGORILER", lambda: str(kategorileri_listele()), "Tüm skill kategorilerini listele")
        plugin_arac_kaydet("SKILL_OKU", lambda ad="": skill_oku(ad) or f"[Hata]: '{ad}' skill bulunamadi", "Skill içeriğini oku")
    except ImportError:
        pass


def skill_v2_araclari_kaydet(motor) -> None:
    try:
        from skill_utils import (
            skill_aktivat, kategori_skill_listele,
            skill_script_calistir, skill_script_yardim,
            skill_sayisi, skill_olustur, skill_dogrula,
            skill_index_yenile, skill_izin_verilen_araclar,
            skill_eval_ekle, skill_eval_listele,
        )

        def _aktivat_ve_izin_guncelle(ad: str = "") -> str:
            sonuc = skill_aktivat(ad)
            try:
                izinler = skill_izin_verilen_araclar(ad)
                if izinler and hasattr(motor, "ekstra_izin_araclar"):
                    motor.ekstra_izin_araclar.update(izinler)
            except Exception as e:
                log.debug("Skill izin güncelleme hatasi: %s", e)
            return sonuc

        plugin_arac_kaydet("SKILL_AKTIVAT", _aktivat_ve_izin_guncelle, "Skill'i aktive et")
        plugin_arac_kaydet("SKILL_KATEGORI", lambda kat="": str(kategori_skill_listele(kat)), "Kategorideki skill listesi")
        plugin_arac_kaydet("SKILL_SCRIPT", lambda skill="", script="", arglar="": skill_script_calistir(skill, script, arglar), "Skill scripti calistir")
        plugin_arac_kaydet("SKILL_OLUSTUR", lambda ad="", aciklama="", talimatlar="", kategori="": skill_olustur(ad, aciklama, talimatlar, kategori), "Yeni skill olustur")
        plugin_arac_kaydet("SKILL_DOGRULA", lambda ad="": skill_dogrula(ad), "Skill dogrula")
        plugin_arac_kaydet("SKILL_INDEX_YENILE", lambda: f"[Index]: {skill_index_yenile(zorla=True)} skill guncellendi.", "FTS5 index yenile")
        plugin_arac_kaydet("SKILL_SCRIPT_YARDIM", lambda skill="", script="": skill_script_yardim(skill, script), "Script yardim")
        plugin_arac_kaydet("SKILL_EVAL_EKLE", lambda ad="", prompt="", expected="", assertions="": skill_eval_ekle(ad, prompt, expected, [a.strip() for a in assertions.split("|") if a.strip()] if assertions else []), "Eval test case ekle")
        plugin_arac_kaydet("SKILL_EVAL_LISTELE", lambda ad="": skill_eval_listele(ad), "Eval listele")
        try:
            log.info("Skill v4: %s skill yuklu.", skill_sayisi())
        except Exception:
            pass
    except ImportError:
        pass


def hafiza_araclari_kaydet(motor) -> None:
    try:
        from memory_agent import hafiza_kur, hafiza_sifirla
        plugin_arac_kaydet("HAFIZA_DURUMU", lambda: str(hafiza_kur().info()), "Konusma hafiza durumu")
        plugin_arac_kaydet("HAFIZA_TEMIZLE", lambda: (hafiza_sifirla(), "Hafiza temizlendi.")[1], "Hafiza temizle")
        plugin_arac_kaydet("HAFIZA_KAYDET", lambda: (hafiza_kur().save_memory(), "Hafiza kaydedildi.")[1], "Hafiza kaydet")
    except ImportError:
        pass


def hook_tetikle(motor, arac: str, params: list, sonuc: str) -> None:
    if not getattr(motor, "_hooks", None):
        return
    hata = "[Hata]" in sonuc or "[hata]" in sonuc.lower()
    olay = "TOOL_ERROR" if hata else "TOOL_CALLED"
    motor._hooks.tetikle(olay, arac=arac, params=params, sonuc=sonuc[:200])
