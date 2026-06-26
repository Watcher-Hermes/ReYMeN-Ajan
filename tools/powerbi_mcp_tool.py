# -*- coding: utf-8 -*-
"""
powerbi_mcp_tool.py — ReYMeN Power BI MCP Tool

Power BI Desktop'taki semantic modellere MCP üzerinden bağlanır.
Doğal dil ile DAX formülleri yazdırır, tabloları listeler, sorgu çalıştırır.

Kullanım:
    from tools.powerbi_mcp_tool import PowerBIMCPTool
    pbi = PowerBIMCPTool()
    pbi.connect()
    tablolar = pbi.list_tables()
    pbi.query("EVALUATE 'Satis'")
    pbi.disconnect()

Bağımlılıklar:
    - Power BI Desktop (açık ve bir .pbix dosyası yüklü)
    - powerbi-modeling-mcp MCP server (VS Code extension)
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Varsayılan yapılandırma ──────────────────────────────────────────────────

_DEFAULT_MCP_EXE = (
    "analysis-services.powerbi-modeling-mcp-0.4.0-win32-x64"
)
_VSCODE_EXTENSIONS = Path.home() / ".vscode" / "extensions"
_MCP_SERVER_DIR = _VSCODE_EXTENSIONS / _DEFAULT_MCP_EXE / "server"
_MCP_SERVER_EXE = _MCP_SERVER_DIR / "powerbi-modeling-mcp.exe"


class PowerBIMCPError(Exception):
    """Power BI MCP işlem hatası."""


class PowerBIMCPTool:
    """
    Power BI MCP aracılığıyla semantic modellere bağlanma.

    Örnek:
        pbi = PowerBIMCPTool()
        if pbi.connect():
            print(pbi.list_tables())
            print(pbi.query("EVALUATE DimDate"))
            pbi.disconnect()
    """

    def __init__(self, mcp_exe_path: Optional[Path] = None):
        self._process: Optional[subprocess.Popen] = None
        self._connected = False
        self._mcp_exe = mcp_exe_path or _MCP_SERVER_EXE

    # ── MCP Sunucu Yönetimi ──────────────────────────────────────────────────

    def _mcp_yolunu_bul(self) -> Optional[Path]:
        """MCP server executable'ini bul.

        Önce varsayılan yolu dene, bulamazsa VS Code extensions'da tara.
        """
        if self._mcp_exe.exists():
            return self._mcp_exe

        # VS Code extensions altında tara
        if _VSCODE_EXTENSIONS.exists():
            for ext_dir in _VSCODE_EXTENSIONS.iterdir():
                if "powerbi-modeling-mcp" in ext_dir.name:
                    server_exe = ext_dir / "server" / "powerbi-modeling-mcp.exe"
                    if server_exe.exists():
                        logger.info("MCP server bulundu: %s", server_exe)
                        return server_exe

        logger.warning("Power BI MCP server bulunamadi: %s", self._mcp_exe)
        return None

    def connect(self) -> bool:
        """Power BI MCP sunucusuna bağlan.

        Ön koşul: Power BI Desktop açık ve bir .pbix dosyası yüklü olmalı.

        Returns:
            bool: Bağlantı başarılı mı?
        """
        mcp_path = self._mcp_yolunu_bul()
        if not mcp_path:
            logger.error(
                "Power BI MCP server bulunamadi. "
                "VS Code extension yuklu mu? "
                "Beklenen yol: %s", _MCP_SERVER_EXE
            )
            return False

        try:
            self._process = subprocess.Popen(
                [str(mcp_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            self._connected = True
            logger.info("Power BI MCP baglantisi basarili: %s", mcp_path)
            return True
        except FileNotFoundError:
            logger.error("MCP server exe bulunamadi: %s", mcp_path)
            return False
        except Exception as e:
            logger.error("MCP baglanti hatasi: %s", e)
            return False

    def disconnect(self) -> None:
        """MCP sunucusuyla bağlantıyı kapat."""
        if self._process:
            self._process.terminate()
            self._process.wait(timeout=5)
            self._process = None
        self._connected = False
        logger.info("Power BI MCP baglantisi kapatildi.")

    # ── Sorgu İşlemleri ──────────────────────────────────────────────────────

    def query(self, dax_query: str) -> dict:
        """DAX sorgusu çalıştır.

        Args:
            dax_query: DAX sorgusu (ör: "EVALUATE DimDate")

        Returns:
            dict: Sorgu sonucu ({"success": bool, "data": ..., "error": ...})
        """
        if not self._connected or not self._process:
            return {"success": False, "error": "MCP baglantisi yok. Once connect() cagir."}

        try:
            # JSON-RPC 2.0 isteği
            request = {
                "jsonrpc": "2.0",
                "method": "query",
                "params": {"dax": dax_query},
                "id": 1,
            }
            self._process.stdin.write(json.dumps(request) + "\n")
            self._process.stdin.flush()

            yanit = self._process.stdout.readline()
            if not yanit:
                return {"success": False, "error": "MCP sunucusu yanit vermedi."}

            sonuc = json.loads(yanit)
            if "error" in sonuc:
                return {"success": False, "error": sonuc["error"]}
            return {"success": True, "data": sonuc.get("result", {})}

        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON cozulemedi: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Sorgu hatasi: {e}"}

    def list_tables(self) -> list:
        """Power BI modelindeki tabloları listele.

        Returns:
            list: Tablo isimleri listesi
        """
        sonuc = self.query("EVALUATE INFORMATION_SCHEMA.TABLES")
        if sonuc["success"]:
            tablolar = []
            for row in sonuc.get("data", []):
                if isinstance(row, dict):
                    tablolar.append(row.get("TABLE_NAME", str(row)))
                else:
                    tablolar.append(str(row))
            return tablolar
        return []

    def list_measures(self) -> list:
        """Modeldeki ölçüleri listele.

        Returns:
            list: Ölçü isimleri
        """
        sonuc = self.query(
            "EVALUATE INFORMATION_SCHEMA.MEASURES"
        )
        if sonuc["success"]:
            measures = []
            for row in sonuc.get("data", []):
                if isinstance(row, dict):
                    measures.append(row.get("MEASURE_NAME", str(row)))
                else:
                    measures.append(str(row))
            return measures
        return []

    # ── Durum ─────────────────────────────────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        """Bağlantı durumu."""
        return self._connected

    def status(self) -> dict:
        """Tool durum raporu."""
        return {
            "connected": self._connected,
            "mcp_exe": str(self._mcp_exe),
            "mcp_exists": self._mcp_exe.exists(),
            "powerbi_running": self._powerbi_kontrol(),
        }

    @staticmethod
    def _powerbi_kontrol() -> bool:
        """Power BI Desktop çalışıyor mu?"""
        try:
            import subprocess
            if sys.platform == "win32":
                cikti = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq PBIDesktop.exe"],
                    capture_output=True, text=True, timeout=5
                )
                return "PBIDesktop.exe" in cikti.stdout
            return False
        except Exception:
            return False


# ── CLI Giriş Noktası ─────────────────────────────────────────────────────────

def run(islem: str = "status", dax: str = "") -> str:
    """Power BI MCP tool CLI giriş noktası.

    Args:
        islem: "status", "tables", "measures", "query", "connect", "disconnect"
        dax: query işlemi için DAX sorgusu

    Returns:
        str: JSON formatında sonuç
    """
    pbi = PowerBIMCPTool()

    if islem == "status":
        return json.dumps(pbi.status(), ensure_ascii=False, indent=2)

    if islem in ("tables", "measures", "query") and not pbi.is_connected:
        if not pbi.connect():
            return json.dumps(
                {"success": False, "error": "Power BI MCP baglanamadi."},
                ensure_ascii=False
            )

    if islem == "connect":
        basarili = pbi.connect()
        return json.dumps({"success": basarili}, ensure_ascii=False)

    elif islem == "disconnect":
        pbi.disconnect()
        return json.dumps({"success": True}, ensure_ascii=False)

    elif islem == "tables":
        tablolar = pbi.list_tables()
        return json.dumps(
            {"success": True, "tables": tablolar, "count": len(tablolar)},
            ensure_ascii=False, indent=2
        )

    elif islem == "measures":
        measures = pbi.list_measures()
        return json.dumps(
            {"success": True, "measures": measures, "count": len(measures)},
            ensure_ascii=False, indent=2
        )

    elif islem == "query":
        if not dax:
            return json.dumps(
                {"success": False, "error": "DAX sorgusu gerekli. Ornek: --dax 'EVALUATE DimDate'"},
                ensure_ascii=False
            )
        sonuc = pbi.query(dax)
        return json.dumps(sonuc, ensure_ascii=False, indent=2)

    else:
        return json.dumps(
            {
                "success": False,
                "error": f"Bilinmeyen islem: {islem}. "
                         f"Secenekler: status, connect, disconnect, tables, measures, query"
            },
            ensure_ascii=False
        )


if __name__ == "__main__":
    # Test
    import sys
    args = sys.argv[1:]
    islem = args[0] if args else "status"
    dax = args[1] if len(args) > 1 else ""
    print(run(islem, dax))
