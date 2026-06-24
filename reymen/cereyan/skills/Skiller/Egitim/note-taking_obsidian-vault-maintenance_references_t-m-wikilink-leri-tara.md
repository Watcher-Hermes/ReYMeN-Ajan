# Tüm wikilink'leri tara
for md in sorted(all_md):
    content = md.read_text(encoding="utf-8", errors="replace")
    found = re.findall(r'\[\[([^\]|#]+?)(?:[|#][^\]]*)?\]\]', content)
    for link in found: