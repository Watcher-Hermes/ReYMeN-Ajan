# -*- coding: utf-8 -*-
"""
vision_analyze_tool.py — Görsel analiz aracı.

Hermes Agent vision_analyze_tool karşılığı.
Görsel URL veya dosya yolundan görseli yükler, metin/soru ile analiz eder.
OCR, nesne tanıma, içerik açıklama.

Kurulum: pip install pillow requests base64
    (opsiyonel: pip install transformers torch — derin analiz için)

Kullanım:
    from reymen.arac.vision_analyze_tool import vision_analyze
    sonuc = vision_analyze("https://example.com/image.png", "Bu görselde ne var?")
"""

import base64
import io
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Optional, Dict

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def _gorsel_yukle(image_url: str) -> bytes:
    """Görseli URL veya dosya yolundan yükler."""
    if image_url.startswith(("http://", "https://")):
        req = urllib.request.Request(image_url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    elif image_url.startswith("data:"):
        # data:image/png;base64,xxxx
        data = image_url.split(",", 1)[1]
        return base64.b64decode(data)
    else:
        # Yerel dosya
        path = Path(image_url).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Görsel dosyası bulunamadı: {image_url}")
        return path.read_bytes()


def _gorsel_boyut_al(data: bytes) -> tuple:
    """Görsel boyutlarını döner (width, height)."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data))
        return img.size
    except Exception:
        return (0, 0)


def _gorsel_format_al(data: bytes) -> str:
    """Görsel formatını tespit eder."""
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return "PNG"
    elif data[:2] == b'\xff\xd8':
        return "JPEG"
    elif data[:4] == b'GIF8':
        return "GIF"
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return "WEBP"
    elif data[:4] == b'%PDF':
        return "PDF"
    return "UNKNOWN"


def _ocr_yap(data: bytes, dil: str = "tr,en") -> str:
    """EasyOCR ile metin çıkarma."""
    try:
        import easyocr
        import numpy as np
        from PIL import Image

        img = Image.open(io.BytesIO(data)).convert("RGB")
        img_array = np.array(img)

        diller = [d.strip() for d in dil.split(",")]
        reader = easyocr.Reader(diller, gpu=False)
        sonuclar = reader.readtext(img_array)

        metinler = []
        for (bbox, text, conf) in sonuclar:
            if conf > 0.3:
                metinler.append(f"{text} ({conf:.0%})")

        return "\n".join(metinler) if metinler else "[OCR]: Metin bulunamadı."
    except ImportError:
        return "[OCR]: EasyOCR kurulu değil (pip install easyocr)."
    except Exception as e:
        return f"[OCR Hatası]: {e}"


def _gorsel_acikla(data: bytes, question: Optional[str] = None) -> str:
    """Görseli açıklar (basit mod — boyut, format, renk analizi)."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(data)).convert("RGB")
        w, h = img.size

        # Temel renk analizi
        img_small = img.resize((50, 50))
        pixels = list(img_small.getdata())
        avg_r = sum(p[0] for p in pixels) // len(pixels)
        avg_g = sum(p[1] for p in pixels) // len(pixels)
        avg_b = sum(p[2] for p in pixels) // len(pixels)

        # Dominant renk
        if avg_r > 180 and avg_g < 100 and avg_b < 100:
            renk = "kırmızı tonlarında"
        elif avg_r < 100 and avg_g > 180 and avg_b < 100:
            renk = "yeşil tonlarında"
        elif avg_r < 100 and avg_g < 100 and avg_b > 180:
            renk = "mavi tonlarında"
        elif avg_r > 180 and avg_g > 180 and avg_b > 180:
            renk = "açık/beyaz tonlarında"
        elif avg_r < 80 and avg_g < 80 and avg_b < 80:
            renk = "koyu/siyah tonlarında"
        else:
            renk = f"karışık tonlarda (R:{avg_r} G:{avg_g} B:{avg_b})"

        # Parlaklık
        parlaklik = (avg_r * 0.299 + avg_g * 0.587 + avg_b * 0.114)
        parlaklik_str = "parlak" if parlaklik > 150 else "karanlık" if parlaklik < 80 else "orta parlaklıkta"

        format_str = _gorsel_format_al(data)
        boyut_kb = len(data) / 1024

        aciklama = (
            f"**Görsel Analiz:**\n"
            f"- Boyut: {w}x{h} piksel\n"
            f"- Format: {format_str}\n"
            f"- Dosya: {boyut_kb:.1f} KB\n"
            f"- Dominant renk: {renk}\n"
            f"- Parlaklık: {parlaklik_str}\n"
        )

        if question:
            # OCR ile soruyu cevaplamaya çalış
            ocr_sonuc = _ocr_yap(data)
            if "[OCR]" not in ocr_sonuc:
                aciklama += f"\n**OCR ile okunan metin:**\n{ocr_sonuc}\n"
            aciklama += f"\n**Soru:** {question}\n"
            aciklama += "**Not:** Derin analiz için `transformers` kütüphanesi gerekir.\n"

        return aciklama

    except ImportError:
        return f"[Analiz]: Pillow kurulu değil. Boyut: {len(data)} byte."
    except Exception as e:
        return f"[Analiz Hatası]: {e}"


def vision_analyze(image_url: str, question: Optional[str] = None,
                   ocr: bool = True, dil: str = "tr,en") -> Dict:
    """
    Görseli analiz eder.

    Args:
        image_url: Görsel URL'si, dosya yolu veya data URL
        question: Görsel hakkında soru (opsiyonel)
        ocr: OCR ile metin çıkarma
        dil: OCR dili (varsayılan: tr,en)

    Returns:
        {"description", "ocr_text", "metadata", "error"}
    """
    try:
        data = _gorsel_yukle(image_url)
    except Exception as e:
        return {"description": "", "ocr_text": "", "metadata": {}, "error": str(e)}

    # Metadata
    metadata = {
        "size_bytes": len(data),
        "format": _gorsel_format_al(data),
        "dimensions": _gorsel_boyut_al(data),
        "source": image_url[:200],
    }

    # Açıklama
    description = _gorsel_acikla(data, question)

    # OCR
    ocr_text = ""
    if ocr:
        ocr_text = _ocr_yap(data, dil)

    return {
        "description": description,
        "ocr_text": ocr_text,
        "metadata": metadata,
        "error": None,
    }


def run(image_url: str = "", question: str = "", ocr: str = "true",
        dil: str = "tr,en") -> str:
    """
    Motor entegrasyonu için run fonksiyonu.
    """
    if not image_url or not image_url.strip():
        return "[Hata]: image_url parametresi boş olamaz."

    ocr_flag = ocr.lower() in ("true", "1", "evet", "yes")
    sonuc = vision_analyze(image_url.strip(), question=question or None,
                           ocr=ocr_flag, dil=dil)

    if sonuc.get("error"):
        return f"[Hata]: {sonuc['error']}"

    cikti = sonuc["description"]
    if sonuc.get("ocr_text") and "[OCR]" not in sonuc["ocr_text"]:
        cikti += f"\n\n**OCR Metin:**\n{sonuc['ocr_text']}"

    # Metadata
    md = sonuc.get("metadata", {})
    cikti += f"\n\n---\n*Format: {md.get('format', '?')} | {md.get('dimensions', (0,0))[0]}x{md.get('dimensions', (0,0))[1]} | {md.get('size_bytes', 0)/1024:.1f} KB*"

    return cikti


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python vision_analyze_tool.py <gorsel_url> [soru]")
        sys.exit(1)

    url = sys.argv[1]
    soru = sys.argv[2] if len(sys.argv) > 2 else ""
    sonuc = vision_analyze(url, question=soru)
    print(sonuc["description"])
    if sonuc["ocr_text"]:
        print(f"\nOCR: {sonuc['ocr_text']}")
