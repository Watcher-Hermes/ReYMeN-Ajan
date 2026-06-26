# -*- coding: utf-8 -*-
"""
n8n_tool.py — ReYMeN n8n Entegrasyon Tool

n8n workflow'larını tetikleme, durum sorgulama, bridge API ile iletişim.

Kullanım:
    from tools.n8n_tool import N8NTool
    n8n = N8NTool()
    n8n.trigger_workflow("workflow_id")
    print(n8n.health_check())

Bağımlılıklar:
    - requests (pip install requests)
    - n8n sunucusu (http://localhost:5678)
"""

import json
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class N8NError(Exception):
    """n8n işlem hatası."""


class N8NTool:
    """n8n workflow yönetim aracı.

    Örnek:
        n8n = N8NTool(base_url="http://localhost:5678")
        if n8n.health_check():
            n8n.trigger_workflow("abc123", {"mesaj": "merhaba"})
    """

    def __init__(
        self,
        base_url: str = "http://localhost:5678",
        api_key: Optional[str] = None,
        bridge_url: str = "http://127.0.0.1:15680",
    ):
        self._base_url = base_url.rstrip("/")
        self._bridge_url = bridge_url.rstrip("/")
        self._headers = {"Content-Type": "application/json"}
        if api_key:
            self._headers["X-N8N-API-KEY"] = api_key
        self._session = requests.Session()
        self._session.headers.update(self._headers)

    # ── n8n API ─────────────────────────────────────────────────────────────

    def health_check(self) -> bool:
        """n8n sunucu sağlık kontrolü.

        Returns:
            bool: Sunucu çalışıyor mu?
        """
        try:
            r = self._session.get(f"{self._base_url}/healthz", timeout=5)
            return r.status_code == 200
        except requests.ConnectionError:
            logger.warning("n8n baglantisi yok: %s", self._base_url)
            return False
        except Exception as e:
            logger.warning("n8n health check hatasi: %s", e)
            return False

    def trigger_workflow(
        self, workflow_id: str, data: Optional[dict] = None
    ) -> dict:
        """n8n workflow'unu tetikle (webhook trigger).

        Args:
            workflow_id: Workflow ID'si veya webhook URL'i
            data: Workflow'a gönderilecek veri

        Returns:
            dict: {"success": bool, "result": ..., "error": ...}
        """
        if not self.health_check():
            return {"success": False, "error": "n8n sunucusu calismiyor."}

        try:
            # Webhook URL'ine POST
            webhook_url = (
                f"{self._base_url}/webhook/{workflow_id}"
                if not workflow_id.startswith("http")
                else workflow_id
            )
            r = self._session.post(
                webhook_url,
                json=data or {},
                timeout=30,
            )
            if r.status_code in (200, 201):
                return {"success": True, "result": r.json() if r.text else {}}
            return {"success": False, "error": f"HTTP {r.status_code}: {r.text[:300]}"}
        except requests.Timeout:
            return {"success": False, "error": "Workflow zaman asimi (30sn)."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_workflows(self) -> list:
        """n8n'deki workflow'ları listele.

        Returns:
            list: Workflow listesi (id, name, active, createdAt)
        """
        try:
            r = self._session.get(
                f"{self._base_url}/rest/workflows",
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                workflows = []
                for wf in data.get("data", []):
                    workflows.append({
                        "id": wf.get("id"),
                        "name": wf.get("name"),
                        "active": wf.get("active", False),
                        "created": wf.get("createdAt", ""),
                    })
                return workflows
            return []
        except Exception as e:
            logger.warning("Workflow listeleme hatasi: %s", e)
            return []

    def get_workflow_status(self, workflow_id: str) -> dict:
        """Workflow durumunu sorgula.

        Args:
            workflow_id: Workflow ID'si

        Returns:
            dict: Workflow durumu
        """
        try:
            r = self._session.get(
                f"{self._base_url}/rest/workflows/{workflow_id}",
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json().get("data", {})
                return {
                    "success": True,
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "active": data.get("active", False),
                    "tags": [t.get("name", "") for t in data.get("tags", [])],
                }
            return {"success": False, "error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Bridge API (ReYMeN özel) ────────────────────────────────────────────

    def bridge_health(self) -> bool:
        """Bridge API sağlık kontrolü."""
        try:
            r = requests.get(f"{self._bridge_url}/health", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def bridge_queue_message(self, chat_id: str, message: str) -> dict:
        """Bridge API'ye mesaj kuyruğuna ekle.

        Args:
            chat_id: Telegram chat ID'si
            message: Gönderilecek mesaj

        Returns:
            dict: İşlem sonucu
        """
        try:
            r = requests.post(
                f"{self._bridge_url}/_bridge/queue/{chat_id}.json",
                json={"text": message},
                timeout=10,
            )
            if r.status_code == 200:
                return {"success": True, "result": r.json()}
            return {"success": False, "error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def bridge_get_answer(self, chat_id: str) -> dict:
        """Bridge API'den cevap al."""
        try:
            r = requests.get(
                f"{self._bridge_url}/_bridge/answers/{chat_id}.json",
                timeout=10,
            )
            if r.status_code == 200:
                return {"success": True, "data": r.json()}
            return {"success": False, "error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ── CLI Giriş Noktası ─────────────────────────────────────────────────────────

def run(islem: str = "status", workflow_id: str = "", data: str = "") -> str:
    """n8n Tool CLI giriş noktası.

    Args:
        islem: "status", "trigger", "list", "workflows", "bridge"
        workflow_id: Workflow ID'si (trigger için)
        data: JSON string (trigger için)

    Returns:
        str: JSON formatında sonuç
    """
    n8n = N8NTool()

    if islem == "status":
        saglik = n8n.health_check()
        bridge = n8n.bridge_health()
        workflows = n8n.list_workflows()
        return json.dumps(
            {
                "n8n_running": saglik,
                "bridge_running": bridge,
                "workflow_count": len(workflows),
                "workflows": workflows[:10],
            },
            ensure_ascii=False, indent=2
        )

    elif islem == "trigger":
        if not workflow_id:
            return json.dumps(
                {"success": False, "error": "workflow_id gerekli."},
                ensure_ascii=False
            )
        payload = json.loads(data) if data else {}
        sonuc = n8n.trigger_workflow(workflow_id, payload)
        return json.dumps(sonuc, ensure_ascii=False, indent=2)

    elif islem in ("list", "workflows"):
        workflows = n8n.list_workflows()
        return json.dumps(
            {"success": True, "workflows": workflows, "count": len(workflows)},
            ensure_ascii=False, indent=2
        )

    elif islem == "bridge":
        # Bridge durumu
        return json.dumps(
            {"bridge_running": n8n.bridge_health()},
            ensure_ascii=False
        )

    else:
        return json.dumps(
            {
                "success": False,
                "error": f"Bilinmeyen islem: {islem}. "
                         f"Secenekler: status, trigger, list, workflows, bridge"
            },
            ensure_ascii=False
        )


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    islem = args[0] if args else "status"
    wid = args[1] if len(args) > 1 else ""
    payload = args[2] if len(args) > 2 else ""
    print(run(islem, wid, payload))
