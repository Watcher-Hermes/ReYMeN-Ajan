# Type a command and press Enter
"$VBOX" controlvm "$VM" keyboardputstring "echo Merhaba, ben Hermes"
"$VBOX" controlvm "$VM" keyboardputstring $'\n'