---
name: technical-reference-generator
title: Technical Reference Document Generator
description: "Generate structured technical reference documents (Q&A pairs, architecture docs, migration guides) from live codebase analysis. Scans actual project structure first, then produces grounded copy-pasteable output."
tags: [documentation, technical-writing, codebase-analysis, reference, turkish]
category: productivity
audience: user
---

# Technical Reference Generator

Generate structured technical reference documents from a live codebase. Output is copy-pasteable, sectioned, and grounded in real file paths.

## When to Use

- User asks for "X teknik soru-cevap", "X hakkında referans belgesi", "architecture doc", "Q&A pairs"
- User wants structured technical documentation about a system/project
- User asks to document how a system works internally (file structures, workflows, architecture)
- Large content generation task that benefits from subagent delegation

## Workflow

### 1. Scan Actual Project Structure (CRITICAL — do not skip)

Before generating ANY content, scan the real project:

```bash
# Directory tree (2-3 levels deep)
find <project_root> -maxdepth 3 -type d | head -60

# Key config files
cat <project_root>/config.yaml  # or config.json, .env, etc.

# Identity/behavior files
cat <project_root>/SOUL.md  # or AGENTS.md, CLAUDE.md

# Decision/notes files
cat <project_root>/decisions.md  # or README.md, CHANGELOG

# Python modules
find <project_root> -name "*.py" -maxdepth 2 | head -30

# Skills/tools structure
find <project_root> -name "SKILL.md" -maxdepth 3 | head -20
```

**PITFALL: If you generate technical documentation WITHOUT scanning the real structure, you WILL hallucinate file paths, module names, and architecture details. The output will look plausible but be wrong.** Always ground in real data.

### 2. Gather Technical Details

Read key files to understand:
- Config structure (what settings exist, what they control)
- Module organization (which files handle which concerns)
- Data flow (how components connect)
- Key patterns (learning loops, memory systems, tool chains)

### 3. Plan Document Structure

Organize by topic sections. For Q&A format:
- Group questions by theme (architecture, memory, skills, tools, etc.)
- Each question targets one specific mechanism
- Each answer includes: what it is, how it works, which files are involved

### 4. Generate Content (delegate if large)

For 50+ items, delegate to a subagent with all gathered context:

```
goal: Write [N] technical Q&A pairs about [system]...
context: [all scanned file paths, config contents, module lists]
toolsets: ["file", "terminal"]
```

### 5. Verify Output

- Spot-check that file paths mentioned in the document actually exist
- Verify line counts, section counts, and formatting
- Confirm the output is copy-pasteable (no broken markdown)

## Output Format (Q&A)

Each Q&A entry:

```markdown
### SORU [N]: [Question]
**CEVAP:** [Detailed technical answer — what it is, how it works]
**YOL (Akış/Dosya):** [File paths and workflow — which files connect, data flow]
```

## Output Format (General Reference)

```markdown
# [Title]
> [Context line]

## SECTION 1: [Topic]
### [Subtopic]
[Content with file paths, code examples, architecture details]

## SECTION 2: [Topic]
...
```

## Pitfalls

1. **Hallucinated paths** — Never guess file paths. Always `find` or `ls` first. If a path doesn't exist, say "bulunamadı" instead of making one up.
2. **Generic answers** — User wants SYSTEM-SPECIFIC answers, not textbook definitions. Reference actual config values, actual file names, actual module names.
3. **Missing YOL/AKIŞ section** — The workflow/path section is what makes the output useful for comparison. Always include which files connect and how data flows.
4. **Subagent context loss** — When delegating, pass ALL gathered context (file paths, config contents, module lists) in the `context` field. Subagents have no conversation memory.
5. **Overly long answers** — Keep each answer focused on ONE mechanism. Don't combine multiple topics in a single Q&A.

## Example: Hermes Agent 100 Q&A

Generated `HERMES_TEKNIK_100_SORU.md` (667 lines, 57.7KB):
- Scanned: config.yaml, SOUL.md, decisions.md, .ReYMeN/ (40+ dirs), reymen/ (cereyan, arac, hafiza modules)
- Structure: 10 sections × ~10 questions each
- Format: SORU → CEVAP → YOL (Akış/Dosya)
- Delegated to subagent with full project context
- Verified: 100 SORU entries, all sections present, file paths grounded

## Related

- `skill-cataloging` — Skill export to Obsidian (different use case, but similar scan-first pattern)
- `markdown-viewer` — Diagram/visualization generation (complementary for visual docs)
