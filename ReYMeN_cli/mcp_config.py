# -*- coding: utf-8 -*-
"""ReYMeN_cli/mcp_config.py — MCP CLI Komutlari.

MCP sunucu ayarlari ve yonetimi.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def mcp_list() -> str:
    """Kayitli MCP sunucularini listele."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from mcp_serve import TOOLS
    return f"[MCP] {len(TOOLS)} tool:\n" + "\n".join(f"  - {t['name']}" for t in TOOLS)


def mcp_serve(port: int = 9100) -> str:
    """MCP sunucusunu baslat."""
    import sys
    import threading
    sys.path.insert(0, str(PROJE_KOK))
    from acp_adapter.server import ACPServer
    server = ACPServer(port=port)
    # Araclari kaydet
    from main import AIAgentOrchestrator, CONFIG
    agent = AIAgentOrchestrator(config=CONFIG, max_tur=3)
    server.tool_kaydet("run", lambda args: agent.run_conversation(args.get("hedef", "")))
    server.tool_kaydet("status", lambda args: "hazir")

    t = threading.Thread(target=server.baslat, args=("tcp",), daemon=True)
    t.start()
    return f"[MCP] Sunucu baslatildi: port {port}"


def mcp_test(host: str = "127.0.0.1", port: int = 9100) -> str:
    """MCP sunucusunu test et."""
    import sys
    sys.path.insert(0, str(PROJE_KOK))
    from tools.mcp_tool import MCPClient
    client = MCPClient()
    tools = client.tool_listele(host=host, port=port)
    if tools:
        return f"[MCP] Baglanti basarili. {len(tools)} tool:\n" + "\n".join(f"  - {t['name']}" for t in tools)
    return f"[MCP] Baglanti basarisiz ({host}:{port})."


def mcp_picker(kriter: str = "") -> str:
    """Uygun MCP sunucusu sec.

    Args:
        kriter: "local", "ReYMeN", "codex"

    Returns:
        Onerilen MCP adresi
    """
    oneriler = {
        "local": "127.0.0.1:9100 (ReYMeN ACP)",
        "ReYMeN": "127.0.0.1:9090 (ReYMeN Agent)",
        "codex": "stdio (Codex CLI)",
    }
    if kriter:
        return f"[MCP] Onerilen: {oneriler.get(kriter, 'Bilinmiyor')}"

    satirlar = ["[MCP] Secenekler:"]
    for k, v in oneriler.items():
        satirlar.append(f"  {k:<10} {v}")
    return "\n".join(satirlar)
