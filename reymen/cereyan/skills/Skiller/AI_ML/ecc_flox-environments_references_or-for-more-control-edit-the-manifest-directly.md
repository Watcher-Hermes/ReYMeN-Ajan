# Or for more control, edit the manifest directly
tmp_manifest="$(mktemp)"
flox list -c > "$tmp_manifest"