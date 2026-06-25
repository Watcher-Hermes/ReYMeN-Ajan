# -*- coding: utf-8 -*-
"""
skill_view_manage.py — Skill görme ve yönetme sistemi.
Hermes Agent skill_view/skill_manage karşılığı.

Kullanım:
    from reymen.sistem.skill_view_manage import skill_view, skill_manage, skills_list
    icerik = skill_view("intent-recognition")
    skills_list()
"""

from __future__ import annotations
import logging
log = logging.getLogger(__name__)

import os
import re
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class SkillMeta:
    """Skill metadata."""
    name: str
    path: str
    category: Optional[str] = None
    description: Optional[str] = None
    frontmatter: Dict = None
    body: str = ""

    def __post_init__(self):
        if self.frontmatter is None:
            self.frontmatter = {}


class SkillManager:
    """Skill okuma, listeleme ve yönetme."""

    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            # ReYMeN skill dizini
            proje_kok = Path(__file__).parent.parent.parent
            self.skills_dir = proje_kok / "skills"
        else:
            self.skills_dir = Path(skills_dir)

    def skills_list(self, category: str = None) -> List[SkillMeta]:
        """Tüm skill'leri listele."""
        skills = []
        if not self.skills_dir.exists():
            return skills

        for skil_file in self.skills_dir.rglob("SKILL.md"):
            meta = self._parse_skill(skil_file)
            if meta:
                if category is None or meta.category == category:
                    skills.append(meta)
        return skills

    def skill_view(self, name: str) -> Optional[SkillMeta]:
        """Belirli bir skill'in içeriğini göster."""
        # İsimle ara
        for skil_file in self.skills_dir.rglob("SKILL.md"):
            meta = self._parse_skill(skil_file)
            if meta and meta.name == name:
                return meta

        # Kategori/isim yolunda ara
        for skil_file in self.skills_dir.rglob("SKILL.md"):
            if name.lower() in str(skil_file).lower():
                return self._parse_skill(skil_file)
        return None

    def skill_manage(self, action: str, name: str, content: str = None,
                     category: str = None) -> Dict:
        """Skill yönet: create, patch, edit, delete."""
        skill_dir = self.skills_dir / category / name if category else self.skills_dir / name
        skill_file = skill_dir / "SKILL.md"

        if action == "create":
            if skill_file.exists():
                return {"success": False, "error": f"Skill zaten var: {name}"}
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file.write_text(content or "", encoding="utf-8")
            return {"success": True, "path": str(skill_file)}

        elif action == "patch":
            if not skill_file.exists():
                return {"success": False, "error": f"Skill bulunamadı: {name}"}
            mevcut = skill_file.read_text(encoding="utf-8")
            # Basit string replace (content = eski::yeni formatında)
            if content and "::" in content:
                eski, yeni = content.split("::", 1)
                mevcut = mevcut.replace(eski, yeni)
                skill_file.write_text(mevcut, encoding="utf-8")
                return {"success": True, "path": str(skill_file)}
            return {"success": False, "error": "Patch formatı: 'eski::yeni'"}

        elif action == "edit":
            if not skill_file.exists():
                return {"success": False, "error": f"Skill bulunamadı: {name}"}
            skill_file.write_text(content or "", encoding="utf-8")
            return {"success": True, "path": str(skill_file)}

        elif action == "delete":
            if not skill_file.exists():
                return {"success": False, "error": f"Skill bulunamadı: {name}"}
            skill_file.unlink()
            return {"success": True, "deleted": str(skill_file)}

        return {"success": False, "error": f"Bilinmeyen action: {action}"}

    def _parse_skill(self, skill_file: Path) -> Optional[SkillMeta]:
        """SKILL.md dosyasını parse et."""
        try:
            icerik = skill_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

        # Frontmatter parse
        frontmatter = {}
        body = icerik
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', icerik, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            body = fm_match.group(2)
            for satir in fm_text.split("\n"):
                if ":" in satir:
                    key, val = satir.split(":", 1)
                    frontmatter[key.strip()] = val.strip()

        # Name ve category
        name = frontmatter.get("name", skill_file.parent.name)
        category = None
        parts = skill_file.parts
        if "skills" in parts:
            idx = list(parts).index("skills")
            if idx + 1 < len(parts) - 1:
                category = parts[idx + 1]

        return SkillMeta(
            name=name,
            path=str(skill_file),
            category=category,
            description=frontmatter.get("description", ""),
            frontmatter=frontmatter,
            body=body[:2000],  # İlk 2000 karakter
        )


# ── Global instance ──────────────────────────────────────────────────────
_manager: Optional[SkillManager] = None

def get_manager() -> SkillManager:
    global _manager
    if _manager is None:
        _manager = SkillManager()
    return _manager

def skills_list(category: str = None) -> List[SkillMeta]:
    """Tüm skill'leri listele."""
    return get_manager().skills_list(category)

def skill_view(name: str) -> Optional[SkillMeta]:
    """Skill içeriğini göster."""
    return get_manager().skill_view(name)

def skill_manage(action: str, name: str, content: str = None,
                 category: str = None) -> Dict:
    """Skill yönet."""
    return get_manager().skill_manage(action, name, content, category)
