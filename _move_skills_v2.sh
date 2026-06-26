#!/bin/bash
# Move ALL remaining content from skills/ to Skiller/
# Phase 1: Non-overlapping directories → just mv
# Phase 2: Overlapping directories → merge files
# Phase 3: Flat .md files → mv to root of Skiller/

cd "/c/Users/marko/Desktop/Reymen Proje/hermes_projesi" || exit 1

SRC="skills"
DST="reymen/cereyan/skills/Skiller"

echo "=== Phase 1: Non-overlapping directories ==="
for dir in "$SRC"/*/; do
    [ -e "$dir" ] || continue
    d=$(basename "$dir")
    if [ ! -d "$DST/$d" ]; then
        echo "  MOVE: $d"
        mv "$dir" "$DST/$d"
    fi
done

echo ""
echo "=== Phase 2: Overlapping directories — merge files ==="
for dir in "$SRC"/*/; do
    [ -e "$dir" ] || continue
    d=$(basename "$dir")
    if [ -d "$DST/$d" ]; then
        # Count items in source
        itemcount=$(find "$dir" -mindepth 1 -maxdepth 1 | wc -l)
        [ "$itemcount" -eq 0 ] && { rmdir "$dir" 2>/dev/null; echo "  EMPTY DEL: $d"; continue; }
        # Merge using rsync-style: move only non-existing files
        echo "  MERGING: $d ($itemcount items)"
        for item in "$dir"* "$dir".*; do
            [ -e "$item" ] || continue
            base=$(basename "$item")
            [ "$base" = "." ] || [ "$base" = ".." ] || [ "$base" = "__pycache__" ] && continue
            if [ ! -e "$DST/$d/$base" ]; then
                mv "$item" "$DST/$d/$base"
            fi
        done
        # Remove if empty
        rmdir "$dir" 2>/dev/null || true
    fi
done

echo ""
echo "=== Phase 3: Flat files in skills/ root ==="
for f in "$SRC"/*.md "$SRC"/manifest.json "$SRC"/*.obsolete; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    if [ ! -f "$DST/$base" ]; then
        echo "  MOVE: $base"
        mv "$f" "$DST/$base"
    else
        echo "  SKIP (exists): $base"
        rm "$f"
    fi
done

echo ""
echo "=== Phase 4: Remove skills/ if empty ==="
remaining=$(find "$SRC" -mindepth 1 2>/dev/null | wc -l)
if [ "$remaining" -eq 0 ]; then
    rm -rf "$SRC"
    echo "  REMOVED: skills/ directory"
else
    echo "  WARNING: $remaining items remain in skills/:"
    echo "  Files: $(find "$SRC" -type f | wc -l)"
    echo "  Dirs: $(find "$SRC" -type d -mindepth 1 | wc -l)"
fi

echo ""
echo "=== Final Skiller/ stats ==="
echo "  Files: $(find "$DST" -type f | wc -l)"
echo "  Directories: $(ls -d "$DST"/*/ 2>/dev/null | wc -l)"
