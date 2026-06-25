# -*- coding: utf-8 -*-
"""
file_ops_tool.py — Dosya işlem aracı.

Hermes Agent file operations karşılığı.
patch (fuzzy match), write_file, search_files, read_file.

Kullanım:
    from reymen.arac.file_ops_tool import FileOps
    ops = FileOps()
    ops.patch("dosya.py", "eski_metin", "yeni_metin")
    ops.search_files("pattern", path=".", target="content")
"""

import difflib
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class FileOps:
    """Dosya işlemleri yöneticisi."""

    # ── Okuma ────────────────────────────────────────────────────────────────

    def read_file(self, path: str, offset: int = 1, limit: int = 500) -> Dict:
        """Dosyayı satır numaralı olarak okur."""
        p = Path(path).expanduser()
        if not p.exists():
            return {"error": f"Dosya bulunamadı: {path}", "content": "", "total_lines": 0}

        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            total = len(lines)
            start = max(0, offset - 1)  # 1-indexed → 0-indexed
            end = min(total, start + limit)
            selected = lines[start:end]

            content = "\n".join(f"{i+1}|{l}" for i, l in enumerate(selected, start=start))
            return {"content": content, "total_lines": total, "error": None}
        except Exception as e:
            return {"error": str(e), "content": "", "total_lines": 0}

    # ── Yazma ────────────────────────────────────────────────────────────────

    def write_file(self, path: str, content: str) -> Dict:
        """Dosyayı yazar (üzerine yazar)."""
        p = Path(path).expanduser()
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return {"ok": True, "path": str(p), "size": len(content), "error": None}
        except Exception as e:
            return {"ok": False, "path": str(p), "size": 0, "error": str(e)}

    # ── Patch (Fuzzy Match) ──────────────────────────────────────────────────

    def patch(self, path: str, old_string: str, new_string: str,
              replace_all: bool = False) -> Dict:
        """
        Dosyada bul ve değiştir (fuzzy match).

        9 strateji ile eşleme dener:
        1. Tam eşleşme
        2. Boşluk normalize
        3. Satır içi boşluk normalize
        4. Büyük/küçük harf duyarsız
        5. Satır sonu normalize (CRLF→LF)
        6. Baş/son boşluk normalize
        7. Tab→space normalize
        8. Çoklu boşluk→tek boşluk
        9. Fuzzy ratio > 0.85
        """
        p = Path(path).expanduser()
        if not p.exists():
            return {"error": f"Dosya bulunamadı: {path}", "diff": ""}

        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {"error": str(e), "diff": ""}

        if not old_string:
            return {"error": "old_string boş olamaz.", "diff": ""}

        # Strateji 1: Tam eşleşme
        if old_string in content:
            if replace_all:
                new_content = content.replace(old_string, new_string)
            else:
                new_content = content.replace(old_string, new_string, 1)
            return self._kaydet_diff(p, content, new_content)

        # Strateji 2-8: Normalize eşleşme
        normal_stratejiler = [
            lambda s: re.sub(r'\s+', ' ', s).strip(),                    # Boşluk normalize
            lambda s: re.sub(r'[ \t]+', ' ', s),                         # Satır içi boşluk
            lambda s: s.lower(),                                          # Küçük harf
            lambda s: s.replace('\r\n', '\n').replace('\r', '\n'),        # CRLF normalize
            lambda s: s.strip(),                                          # Baş/son boşluk
            lambda s: s.replace('\t', '  '),                              # Tab→space
            lambda s: re.sub(r' {2,}', ' ', s),                          # Çoklu boşluk
        ]

        for strateji in normal_stratejiler:
            norm_old = strateji(old_string)
            norm_content = strateji(content)
            if norm_old in norm_content:
                # Orijinal pozisyonu bul
                idx = norm_content.find(norm_old)
                if idx >= 0:
                    # Orijinal content'teki karşılığını bul (yaklaşık)
                    original_match = content[idx:idx+len(old_string)]
                    if replace_all:
                        new_content = content.replace(original_match, new_string)
                    else:
                        new_content = content.replace(original_match, new_string, 1)
                    return self._kaydet_diff(p, content, new_content)

        # Strateji 9: Fuzzy ratio
        best_ratio = 0
        best_start = -1
        best_end = -1

        # Satır satır dene
        content_lines = content.split('\n')
        old_lines = old_string.split('\n')

        for i in range(len(content_lines) - len(old_lines) + 1):
            candidate = '\n'.join(content_lines[i:i+len(old_lines)])
            ratio = difflib.SequenceMatcher(None, old_string, candidate).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_start = i
                best_end = i + len(old_lines)

        if best_ratio >= 0.85:
            new_lines = content_lines[:best_start] + [new_string] + content_lines[best_end:]
            new_content = '\n'.join(new_lines)
            return self._kaydet_diff(p, content, new_content)

        return {
            "error": f"Eşleşme bulunamadı (en iyi fuzzy ratio: {best_ratio:.2f}).",
            "diff": ""
        }

    def _kaydet_diff(self, path: Path, old_content: str, new_content: str) -> Dict:
        """Dosyayı kaydeder ve diff döner."""
        try:
            path.write_text(new_content, encoding="utf-8")

            # Unified diff
            old_lines = old_content.splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)
            diff = ''.join(difflib.unified_diff(old_lines, new_lines,
                                                fromfile=f"a/{path.name}",
                                                tofile=f"b/{path.name}"))

            return {"ok": True, "diff": diff, "error": None}
        except Exception as e:
            return {"ok": False, "diff": "", "error": str(e)}

    # ── Arama ────────────────────────────────────────────────────────────────

    def search_files(self, pattern: str, target: str = "content",
                     path: str = ".", file_glob: Optional[str] = None,
                     limit: int = 50, context: int = 0) -> Dict:
        """
        Dosya içeriklerinde veya isimlerinde arama.

        Args:
            pattern: Regex pattern (content) veya glob pattern (files)
            target: "content" (içerikte ara) veya "files" (dosya adı)
            path: Arama dizini
            file_glob: Dosya filtresi (*.py)
            limit: Max sonuç
            context: Eşleşme etrafında kaç satır bağlam

        Returns:
            {"matches": [...], "count": N}
        """
        p = Path(path).expanduser()
        if not p.exists():
            return {"matches": [], "count": 0, "error": f"Dizin bulunamadı: {path}"}

        matches = []

        if target == "files":
            # Dosya adı arama
            for root, dirs, files in os.walk(p):
                # Gizli dizinleri atla
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for fname in files:
                    if re.search(pattern, fname, re.I):
                        full_path = Path(root) / fname
                        matches.append({
                            "path": str(full_path),
                            "name": fname,
                            "size": full_path.stat().st_size,
                            "modified": full_path.stat().st_mtime,
                        })
                        if len(matches) >= limit:
                            return {"matches": matches, "count": len(matches), "error": None}

        else:
            # İçerik arama
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in
                           ('node_modules', '__pycache__', '.git', 'venv', '.venv')]
                for fname in files:
                    if file_glob and not re.match(file_glob.replace('*', '.*'), fname):
                        continue
                    # Binary dosyaları atla
                    if fname.endswith(('.pyc', '.exe', '.dll', '.so', '.bin', '.dat', '.db', '.sqlite')):
                        continue

                    full_path = Path(root) / fname
                    try:
                        lines = full_path.read_text(encoding="utf-8", errors="replace").splitlines()
                    except Exception:
                        continue

                    for i, line in enumerate(lines):
                        if re.search(pattern, line, re.I):
                            match_info = {
                                "path": str(full_path),
                                "line": i + 1,
                                "content": line.strip(),
                            }
                            if context > 0:
                                start = max(0, i - context)
                                end = min(len(lines), i + context + 1)
                                ctx_lines = []
                                for j in range(start, end):
                                    marker = ">>>" if j == i else "   "
                                    ctx_lines.append(f"{marker} {j+1}|{lines[j]}")
                                match_info["context"] = "\n".join(ctx_lines)

                            matches.append(match_info)
                            if len(matches) >= limit:
                                return {"matches": matches, "count": len(matches), "error": None}

        return {"matches": matches, "count": len(matches), "error": None}


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_ops = None

def _get_ops() -> FileOps:
    global _ops
    if _ops is None:
        _ops = FileOps()
    return _ops


def run(islem: str = "read_file", path: str = "", content: str = "",
        old_string: str = "", new_string: str = "", pattern: str = "",
        target: str = "content", file_glob: str = "", offset: int = 1,
        limit: int = 500, context: int = 0, replace_all: bool = False) -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: read_file/write_file/patch/search_files
    """
    ops = _get_ops()

    if islem == "read_file":
        if not path:
            return "[Hata]: path parametresi gerekli."
        sonuc = ops.read_file(path, offset=offset, limit=limit)
        if sonuc.get("error"):
            return f"[Hata]: {sonuc['error']}"
        return sonuc["content"]

    elif islem == "write_file":
        if not path:
            return "[Hata]: path parametresi gerekli."
        sonuc = ops.write_file(path, content)
        if sonuc.get("error"):
            return f"[Hata]: {sonuc['error']}"
        return f"✅ Dosya yazıldı: {sonuc['path']} ({sonuc['size']} karakter)"

    elif islem == "patch":
        if not path or not old_string:
            return "[Hata]: path ve old_string gerekli."
        sonuc = ops.patch(path, old_string, new_string, replace_all=replace_all)
        if sonuc.get("error"):
            return f"[Hata]: {sonuc['error']}"
        return f"✅ Patch uygulandı.\n{sonuc['diff']}"

    elif islem == "search_files":
        if not pattern:
            return "[Hata]: pattern parametresi gerekli."
        sonuc = ops.search_files(pattern, target=target, path=path or ".",
                                 file_glob=file_glob or None, limit=limit, context=context)
        if sonuc.get("error"):
            return f"[Hata]: {sonuc['error']}"
        if not sonuc["matches"]:
            return f"🔍 '{pattern}' için sonuç bulunamadı."

        satirlar = [f"🔍 {sonuc['count']} sonuç bulundu:\n"]
        for m in sonuc["matches"]:
            if "line" in m:
                satirlar.append(f"  📄 {m['path']}:{m['line']} — {m['content']}")
                if m.get("context"):
                    satirlar.append(f"     {m['context']}")
            else:
                satirlar.append(f"  📁 {m['path']} ({m.get('size', 0)} byte)")
        return "\n".join(satirlar)

    return f"[Hata]: Bilinmeyen islem: {islem}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python file_ops_tool.py <islem> [parametreler]")
        sys.exit(1)
    print(run(islem=sys.argv[1], path=sys.argv[2] if len(sys.argv) > 2 else ""))
