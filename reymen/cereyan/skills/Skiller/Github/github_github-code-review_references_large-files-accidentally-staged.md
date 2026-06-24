# Large files accidentally staged
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10