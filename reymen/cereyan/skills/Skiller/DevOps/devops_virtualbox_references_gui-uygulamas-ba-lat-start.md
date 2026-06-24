# GUI uygulaması başlat (start)
subprocess.run([
    vbox, "guestcontrol", vm, "start",
    "--exe", "/usr/bin/qterminal",
    "--username", user, "--password", pwd
], env=env)