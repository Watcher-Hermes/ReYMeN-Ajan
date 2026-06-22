# Clear screen first
"$VBOX" controlvm "$VM" keyboardputstring "clear"
"$VBOX" controlvm "$VM" keyboardputstring $'\n'
sleep 1