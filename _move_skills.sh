#!/bin/bash
# Move all skills/ category folders to Skiller/, merging without overwriting

cd "/c/Users/marko/Desktop/Reymen Proje/hermes_projesi" || exit 1

SRC="skills"
DST="reymen/cereyan/skills/Skiller"

echo "=== Phase 1: Moving non-overlapping categories ==="
for dir in "$SRC"/*/; do
    dirname=$(basename "$dir")
    if [ ! -d "$DST/$dirname" ]; then
        echo "  MOVE (new): $dirname"
        mv "$dir" "$DST/$dirname"
    fi
done

echo ""
echo "=== Phase 2: Merging overlapping categories ==="
for dir in "$SRC"/*/; do
    [ -e "$dir" ] || continue
    dirname=$(basename "$dir")
    if [ -d "$DST/$dirname" ]; then
        count=0
        skipped=0
        # Move files
        for item in "$dir"* "$dir".*; do
            [ -e "$item" ] || continue
            base=$(basename "$item")
            [ "$base" = "." ] || [ "$base" = ".." ] || [ "$base" = "__pycache__" ] && continue
            if [ -f "$DST/$dirname/$base" ] || [ -d "$DST/$dirname/$base" ]; then
                skipped=$((skipped + 1))
            else
                mv "$item" "$DST/$dirname/$base"
                count=$((count + 1))
            fi
        done
        echo "  MERGE: $dirname (moved=$count, skipped=$skipped)"
        # Remove directory if empty
        rmdir "$dir" 2>/dev/null || true
    fi
done

echo ""
echo "=== Phase 3: Moving INDEX files ==="
if [ -f "$SRC/INDEX.md" ]; then
    if [ ! -f "$DST/INDEX.md" ]; then
        mv "$SRC/INDEX.md" "$DST/INDEX.md"
        echo "  MOVED: INDEX.md"
    else
        echo "  SKIP: INDEX.md already exists in Skiller"
        rm "$SRC/INDEX.md"
    fi
fi
if [ -f "$SRC/INDEX_from_skiller.md" ]; then
    rm "$SRC/INDEX_from_skiller.md"
    echo "  REMOVED: INDEX_from_skiller.md"
fi

echo ""
echo "=== Phase 4: Remove skills/ if empty ==="
if [ -d "$SRC" ]; then
    remaining=$(find "$SRC" -type f 2>/dev/null | wc -l)
    if [ "$remaining" -eq 0 ]; then
        rm -rf "$SRC"
        echo "  REMOVED: skills/ directory (empty)"
    else
        echo "  WARNING: $remaining files remain in skills/:"
        find "$SRC" -type f 2>/dev/null | head -10
    fi
fi

echo ""
echo "=== Phase 5: Count files in Skiller after merge ==="
find "$DST" -type f 2>/dev/null | wc -l
echo "  categories:"
ls -d "$DST"/*/ 2>/dev/null | wc -l
