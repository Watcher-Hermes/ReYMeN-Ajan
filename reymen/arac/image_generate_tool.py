# -*- coding: utf-8 -*-
"""
image_generate_tool.py — Görsel üretme aracı.

Hermes Agent image_generate_tool karşılığı.
FAL.ai, OpenAI DALL-E veya yerel Stable Diffusion ile görsel üretir.

Kurulum: pip install requests pillow
    (Opsiyonel: pip install fal-client  — FAL.ai için)
    (Opsiyonel: pip install openai      — DALL-E için)

Kullanım:
    from reymen.arac.image_generate_tool import image_generate
    sonuc = image_generate("A futuristic Turkish city at sunset")
"""

import base64
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Optional, Dict

# ── Provider Algılama ────────────────────────────────────────────────────────

def _provider_belirle() -> str:
    """Hangi provider'ın kullanılacağını belirle."""
    if os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY"):
        return "fal"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN"):
        return "huggingface"
    return "none"


# ── FAL.ai Provider ──────────────────────────────────────────────────────────

def _fal_uret(prompt: str, aspect_ratio: str = "square",
              negative_prompt: str = "", model: str = "fal-ai/flux/schnell") -> Dict:
    """FAL.ai ile görsel üretir."""
    try:
        import fal_client
        api_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
        if api_key:
            os.environ["FAL_KEY"] = api_key

        arguments = {"prompt": prompt}
        if negative_prompt:
            arguments["negative_prompt"] = negative_prompt
        if aspect_ratio == "landscape":
            arguments["image_size"] = {"width": 1344, "height": 768}
        elif aspect_ratio == "portrait":
            arguments["image_size"] = {"width": 768, "height": 1344}
        else:
            arguments["image_size"] = {"width": 1024, "height": 1024}

        handler = fal_client.submit(model, arguments=arguments)
        result = handler.get()

        if result and "images" in result and result["images"]:
            image_url = result["images"][0].get("url", "")
            return {"url": image_url, "provider": "fal", "error": None}

        return {"url": "", "provider": "fal", "error": "FAL sonuç döndürmedi."}

    except ImportError:
        return {"url": "", "provider": "fal", "error": "fal-client kurulu değil (pip install fal-client)."}
    except Exception as e:
        return {"url": "", "provider": "fal", "error": f"FAL Hatası: {e}"}


# ── OpenAI DALL-E Provider ───────────────────────────────────────────────────

def _openai_uret(prompt: str, size: str = "1024x1024",
                 model: str = "dall-e-3") -> Dict:
    """OpenAI DALL-E ile görsel üretir."""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )

        if response.data:
            image_url = response.data[0].url
            return {"url": image_url, "provider": "openai", "error": None}

        return {"url": "", "provider": "openai", "error": "OpenAI sonuç döndürmedi."}

    except ImportError:
        return {"url": "", "provider": "openai", "error": "openai kurulu değil (pip install openai)."}
    except Exception as e:
        return {"url": "", "provider": "openai", "error": f"OpenAI Hatası: {e}"}


# ── HuggingFace Provider ─────────────────────────────────────────────────────

def _hf_uret(prompt: str, model: str = "stabilityai/stable-diffusion-xl-base-1.0") -> Dict:
    """HuggingFace Inference API ile görsel üretir."""
    try:
        api_key = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
        if not api_key:
            return {"url": "", "provider": "huggingface", "error": "HF_TOKEN bulunamadı."}

        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = json.dumps({"inputs": prompt}).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            img_data = resp.read()

            # Kaydet
            out_dir = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "generated"
            out_dir.mkdir(parents=True, exist_ok=True)
            fname = f"hf_{int(time.time())}.png"
            out_path = out_dir / fname
            out_path.write_bytes(img_data)

            return {"url": str(out_path), "provider": "huggingface", "error": None}

    except Exception as e:
        return {"url": "", "provider": "huggingface", "error": f"HuggingFace Hatası: {e}"}


# ── Görsel İndirme ───────────────────────────────────────────────────────────

def _gorsel_indir(url: str, kayit_yolu: Optional[str] = None) -> str:
    """URL'den görseli indirip yerel dosyaya kaydeder."""
    if not url:
        return ""

    # Zaten yerel dosya
    if not url.startswith("http"):
        return url

    out_dir = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    if kayit_yolu:
        out_path = Path(kayit_yolu)
    else:
        fname = f"gen_{int(time.time())}.png"
        out_path = out_dir / fname

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ReYMeN/2.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            out_path.write_bytes(resp.read())
        return str(out_path)
    except Exception as e:
        return f"[İndirme Hatası]: {e}"


# ── Ana Fonksiyon ────────────────────────────────────────────────────────────

def image_generate(prompt: str, aspect_ratio: str = "square",
                   negative_prompt: str = "", provider: Optional[str] = None,
                   kaydet: bool = True) -> Dict:
    """
    Metin açıklamasından görsel üretir.

    Args:
        prompt: Görsel açıklaması
        aspect_ratio: square/landscape/portrait
        negative_prompt: İstenmeyen öğeler
        provider: fal/openai/huggingface (otomatik algılama)
        kaydet: Görseli yerel dosyaya kaydet

    Returns:
        {"url", "local_path", "provider", "error"}
    """
    if not prompt or not prompt.strip():
        return {"url": "", "local_path": "", "provider": "", "error": "Prompt boş olamaz."}

    provider = provider or _provider_belirle()

    if provider == "fal":
        sonuc = _fal_uret(prompt, aspect_ratio, negative_prompt)
    elif provider == "openai":
        size_map = {"landscape": "1792x1024", "portrait": "1024x1792", "square": "1024x1024"}
        sonuc = _openai_uret(prompt, size=size_map.get(aspect_ratio, "1024x1024"))
    elif provider == "huggingface":
        sonuc = _hf_uret(prompt)
    else:
        return {
            "url": "", "local_path": "", "provider": "",
            "error": "Görsel üretici bulunamadı. FAL_KEY, OPENAI_API_KEY veya HF_TOKEN ayarlayın."
        }

    if sonuc.get("error"):
        return {"url": "", "local_path": "", "provider": sonuc["provider"], "error": sonuc["error"]}

    local_path = ""
    if kaydet and sonuc.get("url"):
        local_path = _gorsel_indir(sonuc["url"])

    return {
        "url": sonuc["url"],
        "local_path": local_path,
        "provider": sonuc["provider"],
        "error": None,
    }


def run(prompt: str = "", aspect_ratio: str = "square",
        negative_prompt: str = "", provider: str = "") -> str:
    """Motor entegrasyonu için run fonksiyonu."""
    if not prompt or not prompt.strip():
        return "[Hata]: prompt parametresi boş olamaz."

    prov = provider if provider else None
    sonuc = image_generate(prompt.strip(), aspect_ratio=aspect_ratio,
                           negative_prompt=negative_prompt, provider=prov)

    if sonuc.get("error"):
        return f"[Hata]: {sonuc['error']}"

    cikti = f"✅ Görsel üretildi ({sonuc['provider']}).\n"
    if sonuc.get("url"):
        cikti += f"URL: {sonuc['url']}\n"
    if sonuc.get("local_path"):
        cikti += f"Dosya: {sonuc['local_path']}\n"

    return cikti


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python image_generate_tool.py <prompt> [aspect_ratio]")
        sys.exit(1)

    prompt = sys.argv[1]
    ar = sys.argv[2] if len(sys.argv) > 2 else "square"
    sonuc = image_generate(prompt, aspect_ratio=ar)
    print(json.dumps(sonuc, indent=2, ensure_ascii=False))
