# Echo a separator
"$VBOX" controlvm "$VM" keyboardputstring "echo ===== TARAMA BASLIYOR ====="
"$VBOX" controlvm "$VM" keyboardputstring $'\n'
sleep 1