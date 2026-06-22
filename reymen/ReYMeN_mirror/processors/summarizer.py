"""
summarizer.py — AI Ozetleme Katmani.

Claude API ile toplanan icerikleri ozetler
ve yapilandirilmis rapor haline getirir.
"""

import os
from typing import Optional

from anthropic import AsyncAnthropic
from loguru import logger

_SYSTEM_PROMPT = """Sen ReYMeN adinda bir bilgi toplama ajanisin.
Sana verilen kaynaklardan bilgi toplayip oz ve guvenilir raporlar uretirsin.

Kurallarin:
- Yalnizca kaynaklarda olan bilgileri kullan
- CeliSen bilgileri belirt
- Her iddia icin kaynak goster
- Turkce ve sade dil kullan"""


class Summarizer:
    """Claude API ile icerik ozetleme."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-6"):
        self.client = AsyncAnthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    async def summarize(self, query: str, contents: list[dict]) -> dict:
        """
        Claude ile icerikleri ozetle ve yapilandir.

        Args:
            query: Arastirma sorusu
            contents: [{"url", "content", ...}, ...]

        Returns:
            {"query", "summary", "sources", "source_count"}
        """
        if not contents:
            return {"query": query, "summary": "Icerik bulunamadi.", "sources": []}

        # Icerikleri birlestir (max 80k karakter — context limiti)
        combined = ""
        sources = []

        for i, item in enumerate(contents[:5], 1):
            if item and item.get("content"):
                combined += f"\n\n--- KAYNAK {i}: {item['url']} ---\n{item['content'][:3000]}"
                sources.append(item["url"])

        user_message = f"""Arastirma sorusu: {query}

Toplanan kaynaklar:
{combined}

Lutfen bu kaynaklari analiz edip kapsamli bir rapor uret:
1. Ana bulgular (3-5 madde)
2. Onemli detaylar
3. Kaynaklar arasi tutarsizliklar (varsa)
4. Guvenilirlik degerlendirmesi"""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )

            summary = response.content[0].text
            logger.info(f"Ozetleme tamamlandi: '{query}'")

            return {
                "query": query,
                "summary": summary,
                "sources": sources,
                "source_count": len(sources),
            }

        except Exception as e:
            logger.error(f"Ozetleme hatasi: {query} -> {e}")
            return {"query": query, "summary": f"Hata: {e}", "sources": sources}


# Kolay kullanim
summarizer = Summarizer()


async def summarize(query: str, contents: list[dict]) -> dict:
    """Kolay kullanim icin wrapper fonksiyon."""
    return await summarizer.summarize(query, contents)
