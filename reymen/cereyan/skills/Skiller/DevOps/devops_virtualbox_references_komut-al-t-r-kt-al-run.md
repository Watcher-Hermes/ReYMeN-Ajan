# Komut çalıştır + çıktı al (run)
r = subprocess.run([
    vbox, "guestcontrol", vm, "run",
    "--exe", "/usr/bin/ls",
    "--username", user, "--password", pwd,
    "--wait-stdout", "--", "-la", "/usr/bin/",
], env=env, capture_output=True, text=True)
print(r.stdout)
```