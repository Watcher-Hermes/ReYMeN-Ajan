# -*- coding: utf-8 -*-
"""ReYMeN_cli/mcp_catalog.py — MCP Katalogu.

Bilinen MCP sunucularinin katalogu ve detaylari.
"""

_MCP_KATALOGU = {
    "ReYMeN": {
        "ad": "ReYMeN ACP",
        "baglanti": "tcp:127.0.0.1:9100",
        "aciklama": "ReYMeN ajaninin ACP sunucusu",
        "tool_ornegii": "run, status, memory_search",
    },
    "ReYMeN": {
        "ad": "ReYMeN Agent",
        "baglanti": "tcp:127.0.0.1:9090",
        "aciklama": "Nous Research ReYMeN Agent MCP",
        "tool_ornegii": "terminal, read_file, web_search",
    },
    "claude": {
        "ad": "Claude Code",
        "baglanti": "stdio:claude mcp",
        "aciklama": "Anthropic Claude Code CLI",
        "tool_ornegii": "Bash, Read, Write, Edit",
    },
    "codex": {
        "ad": "OpenAI Codex CLI",
        "baglanti": "stdio:codex --acp --stdio",
        "aciklama": "OpenAI Codex CLI ACP",
        "tool_ornegii": "run, test, explain",
    },
    "filesystem": {
        "ad": "Filesystem MCP",
        "baglanti": "tcp:127.0.0.1:9000",
        "aciklama": "Dosya sistemi erisim MCP sunucusu",
        "tool_ornegii": "read, write, list, search",
    },
}


def catalog_list() -> str:
    """Katalogdaki MCP sunucularini listele."""
    satirlar = [f"[MCP Catalog] {len(_MCP_KATALOGU)} sunucu:\n"]
    for ad, bilgi in _MCP_KATALOGU.items():
        satirlar.append(f"  {ad:<10} {bilgi['ad']:<20} {bilgi['baglanti']}")
    return "\n".join(satirlar)


def catalog_detail(ad: str) -> str:
    """MCP sunucu detayi."""
    bilgi = _MCP_KATALOGU.get(ad)
    if not bilgi:
        return f"[MCP Catalog] Bilinmiyor: {ad}"
    return (
        f"[MCP Catalog] {bilgi['ad']}\n"
        f"  Baglanti: {bilgi['baglanti']}\n"
        f"  Aciklama: {bilgi['aciklama']}\n"
        f"  Tool ornek: {bilgi['tool_ornegii']}"
    )


def catalog_add(ad: str, baglanti: str, aciklama: str = ""):
    """Kataloga yeni MCP sunucusu ekle."""
    _MCP_KATALOGU[ad] = {
        "ad": ad,
        "baglanti": baglanti,
        "aciklama": aciklama,
        "tool_ornegii": "",
    }
