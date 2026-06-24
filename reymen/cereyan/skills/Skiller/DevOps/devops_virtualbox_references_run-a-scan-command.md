# Run a scan command
"$VBOX" controlvm "$VM" keyboardputstring "sudo nmap -sn 192.168.0.0/24"
"$VBOX" controlvm "$VM" keyboardputstring $'\n'