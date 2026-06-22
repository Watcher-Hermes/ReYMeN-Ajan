# -*- coding: utf-8 -*-
"""ReYMeN_cli/commands.py — Ana CLI Komutlari.

reyment.py'nin ana komutlarini icerir: run, serve, doctor, version.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


class SlashCommandCompleter:
    """Prompt-toolkit completer for slash commands, skills, and bundles."""

    def __init__(self, skill_commands_provider=None, command_filter=None,
                 skill_bundles_provider=None):
        self.skill_commands_provider = skill_commands_provider or (lambda: {})
        self.command_filter = command_filter or (lambda x: True)
        self.skill_bundles_provider = skill_bundles_provider or (lambda: [])

    def get_completions(self, document, complete_event):
        """Yield completions based on current input."""
        from prompt_toolkit.completion import Completion
        text = document.text_before_cursor
        if text.startswith("/"):
            parts = text[1:].split()
            prefix = parts[0].lower() if parts else ""
            commands = self.skill_commands_provider() or {}
            for name in commands:
                if name.lower().startswith(prefix) and self.command_filter(name):
                    yield Completion(f"/{name}", start_position=-len(text))
        else:
            bundles = self.skill_bundles_provider() or []
            for bundle in bundles:
                if isinstance(bundle, str) and bundle.lower().startswith(text.lower()):
                    yield Completion(bundle, start_position=-len(text))


class SlashCommandAutoSuggest:
    """Prompt-toolkit auto-suggestion wrapper combining history + completer."""

    def __init__(self, history_suggest=None, completer=None):
        self.history_suggest = history_suggest
        self.completer = completer

    def get_suggestion(self, buffer, document):
        """Return a suggestion from history or completer."""
        if self.history_suggest:
            try:
                return self.history_suggest.get_suggestion(buffer, document)
            except Exception:
                pass
        return None


def run(hedef: str, max_tur: int = 15) -> str:
    """Ajani calistir.

    Args:
        hedef: Gorev tanimi
        max_tur: Maksimum tur

    Returns:
        Sonuc metni
    """
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from main import AIAgentOrchestrator, CONFIG
    agent = AIAgentOrchestrator(config=CONFIG, max_tur=max_tur)
    sonuc = agent.run_conversation(hedef)
    return sonuc or "[CLI] Gorev tamamlandi."


def serve(port: int = 8080) -> str:
    """Web UI + Gateway baslat."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from start import ReyMenOrkestrator
    ork = ReyMenOrkestrator(port=port, mod="all")
    ork.baslat()
    return "[CLI] Servisler baslatildi."


def doctor() -> str:
    """Sistem teshisi."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from reyment import doctor_komutu
    return doctor_komutu()


def version() -> str:
    """Versiyon bilgisi."""
    return "ReYMeN v1.0.0"


def help_text() -> str:
    """Yardim metni."""
    from . import komut_listele, kategorileri_listele
    satirlar = ["ReYMeN CLI — Kullanim:\n", "  python reyment.py <komut> [argumanlar]\n"]
    for kat in kategorileri_listele():
        satirlar.append(f"\n  [{kat}]")
        for ad, _, yardim in komut_listele(kat):
            satirlar.append(f"    {ad:<25} {yardim}")
    return "\n".join(satirlar)
