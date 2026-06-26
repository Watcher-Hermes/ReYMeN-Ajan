# -*- coding: utf-8 -*-
"""
video_analysis_tool.py — ReYMeN Video Analysis Tool

YouTube videolarından transcript alır, analiz eder, skill çıkarır.
Pipeline:
  1. YouTube URL → transcript + video bilgisi
  2. Metni bölümlere ayır (giriş, teknik adımlar, sonuç)
  3. Her bölümden skill çıkar
  4. Hafızadaki eski bilgiyle karşılaştır

Kullanım:
    from reymen.hermes.tools.video_analysis_tool import VideoAnalysisTool
    vat = VideoAnalysisTool()
    sonuc = vat.analyze("https://youtube.com/watch?v=...")
    print(sonuc)

Bağımlılıklar:
    - yt-dlp (pip install yt-dlp)
    - youtube-transcript-api (pip install youtube-transcript-api)
"""

import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class VideoAnalysisError(Exception):
    """Video analiz işlem hatası."""


class VideoAnalysisTool:
    """
    YouTube videolarını analiz edip skill çıkaran tool.

    Örnek:
        vat = VideoAnalysisTool()
        analiz = vat.analyze("https://youtube.com/watch?v=dQw4w9WgXcQ")
        print(analiz["title"])
        print(analiz["summary"])
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self._output_dir = output_dir or Path.cwd() / "video_analysis"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ── Transcript Çekme ─────────────────────────────────────────────────────

    def get_transcript(self, url: str, lang: str = "tr") -> dict:
        """YouTube videosundan transcript al.

        Önce youtube-transcript-api dene, olmazsa yt-dlp ile altyazı indir.

        Args:
            url: YouTube video URL'si
            lang: Dil kodu (varsayılan: tr)

        Returns:
            dict: {"success": bool, "transcript": str, "segments": [...], "error": ...}
        """
        # 1. youtube-transcript-api dene
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            video_id = self._extract_video_id(url)
            if not video_id:
                return {"success": False, "error": "Video ID çıkarılamadı."}

            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang, "en"])
            metin = " ".join(seg["text"] for seg in transcript_list)
            return {
                "success": True,
                "transcript": metin,
                "segments": transcript_list,
                "source": "youtube_transcript_api",
            }
        except ImportError:
            logger.info("youtube-transcript-api yok, yt-dlp deneniyor...")
        except Exception as e:
            logger.warning("youtube-transcript-api hatasi: %s", e)

        # 2. yt-dlp ile dene
        try:
            video_id = self._extract_video_id(url)
            if not video_id:
                return {"success": False, "error": "Video ID çıkarılamadı."}

            cikti = subprocess.run(
                [
                    sys.executable, "-m", "yt_dlp",
                    "--skip-download",
                    "--write-auto-subs",
                    "--sub-langs", f"{lang},en",
                    "--sub-format", "vtt",
                    "--output", str(self._output_dir / "%(id)s.%(ext)s"),
                    url,
                ],
                capture_output=True, text=True, timeout=120,
            )

            vtt_dosyasi = self._output_dir / f"{video_id}.{lang}.vtt"
            if vtt_dosyasi.exists():
                metin = self._vtt_to_text(vtt_dosyasi)
                return {"success": True, "transcript": metin, "segments": [], "source": "yt-dlp"}
            else:
                return {"success": False, "error": f"Altyazi bulunamadi. Cikti: {cikti.stderr[:500]}"}

        except ImportError:
            return {"success": False, "error": "yt-dlp yuklu degil. pip install yt-dlp"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "yt-dlp zaman asimi (120sn)"}
        except Exception as e:
            return {"success": False, "error": f"yt-dlp hatasi: {e}"}

    def get_video_info(self, url: str) -> dict:
        """YouTube video bilgilerini al.

        Args:
            url: YouTube video URL'si

        Returns:
            dict: {"success": bool, "title": ..., "channel": ..., "duration": ..., ...}
        """
        try:
            cikti = subprocess.run(
                [
                    sys.executable, "-m", "yt_dlp",
                    "--dump-json",
                    "--skip-download",
                    url,
                ],
                capture_output=True, text=True, timeout=30,
            )
            if cikti.returncode != 0:
                return {"success": False, "error": cikti.stderr[:300]}

            bilgi = json.loads(cikti.stdout.strip().split("\n")[0])
            return {
                "success": True,
                "title": bilgi.get("title", ""),
                "channel": bilgi.get("channel", ""),
                "duration": bilgi.get("duration", 0),
                "view_count": bilgi.get("view_count", 0),
                "description": (bilgi.get("description", "") or "")[:500],
                "upload_date": bilgi.get("upload_date", ""),
            }
        except ImportError:
            return {"success": False, "error": "yt-dlp yuklu degil."}
        except json.JSONDecodeError:
            return {"success": False, "error": "JSON cozulemedi."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Analiz ────────────────────────────────────────────────────────────────

    def analyze(self, url: str, lang: str = "tr") -> dict:
        """Videoyu tam analiz et: bilgi + transcript + bölümle.

        Args:
            url: YouTube video URL'si
            lang: Dil kodu

        Returns:
            dict: {
                "success": bool,
                "title": str,
                "channel": str,
                "duration": int,
                "transcript": str (veya varsa),
                "summary": str (AI özeti),
                "sections": [...],
            }
        """
        # Video bilgisi
        info = self.get_video_info(url)
        if not info.get("success"):
            return {"success": False, "error": info.get("error", "Bilgi alinamadi.")}

        # Transcript
        transcript_data = self.get_transcript(url, lang)

        # Bölümle
        sections = []
        transcript = transcript_data.get("transcript", "")
        if transcript:
            sections = self._bolumle(transcript)

        return {
            "success": True,
            "title": info.get("title", ""),
            "channel": info.get("channel", ""),
            "duration": info.get("duration", 0),
            "view_count": info.get("view_count", 0),
            "upload_date": info.get("upload_date", ""),
            "description": info.get("description", ""),
            "transcript": transcript[:5000],  # İlk 5000 karakter
            "transcript_source": transcript_data.get("source", ""),
            "sections": sections,
            "section_count": len(sections),
            "has_transcript": bool(transcript),
        }

    # ── Yardımcı Metodlar ────────────────────────────────────────────────────

    @staticmethod
    def _extract_video_id(url: str) -> Optional[str]:
        """YouTube URL'sinden video ID çıkar."""
        patterns = [
            r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
            r"(?:embed/)([a-zA-Z0-9_-]{11})",
            r"(?:shorts/)([a-zA-Z0-9_-]{11})",
        ]
        for p in patterns:
            match = re.search(p, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _vtt_to_text(vtt_path: Path) -> str:
        """VTT altyazı dosyasını düz metne çevir."""
        import html
        metin = vtt_path.read_text(encoding="utf-8", errors="replace")
        # Zaman damgalarını, WEBVTT başlığını, HTML etiketlerini temizle
        satirlar = []
        for satir in metin.split("\n"):
            s = satir.strip()
            # Zaman damgası satırlarını atla
            if "-->" in s or s.startswith("WEBVTT") or s.startswith("NOTE"):
                continue
            if s and not s.isdigit():
                satirlar.append(html.unescape(s))
        return " ".join(satirlar)

    @staticmethod
    def _bolumle(transcript: str) -> list:
        """Transcript metnini bölümlere ayır (basit heuristic)."""
        sections = []
        # 2000 karakterlik chunk'lara böl
        chunk_size = 2000
        for i in range(0, len(transcript), chunk_size):
            chunk = transcript[i:i + chunk_size].strip()
            if chunk:
                sections.append({
                    "start": i,
                    "end": i + len(chunk),
                    "content": chunk[:500],  # İlk 500 karakter
                })
        return sections


# ── CLI Giriş Noktası ─────────────────────────────────────────────────────────

def run(islem: str = "analyze", url: str = "", lang: str = "tr") -> str:
    """Video Analysis Tool CLI giriş noktası.

    Args:
        islem: "analyze" (tam analiz), "info" (sadece bilgi), "transcript" (sadece metin)
        url: YouTube video URL'si
        lang: Dil kodu (varsayılan: tr)

    Returns:
        str: JSON formatında sonuç
    """
    vat = VideoAnalysisTool()

    if not url:
        return json.dumps(
            {"success": False, "error": "YouTube URL'si gerekli. Ornek: --url 'https://youtube.com/watch?v=...'"},
            ensure_ascii=False
        )

    if islem == "analyze":
        sonuc = vat.analyze(url, lang)
    elif islem == "info":
        sonuc = vat.get_video_info(url)
    elif islem == "transcript":
        sonuc = vat.get_transcript(url, lang)
    else:
        return json.dumps(
            {"success": False, "error": f"Bilinmeyen islem: {islem}. Secenekler: analyze, info, transcript"},
            ensure_ascii=False
        )

    return json.dumps(sonuc, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    islem = args[0] if len(args) > 0 else "analyze"
    url = args[1] if len(args) > 1 else ""
    lang = args[2] if len(args) > 2 else "tr"
    print(run(islem, url, lang))
