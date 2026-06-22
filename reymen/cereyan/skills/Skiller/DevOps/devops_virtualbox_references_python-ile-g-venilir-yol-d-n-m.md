# Python ile güvenilir yol dönüşümü
import subprocess, os

vbox = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
env = {**os.environ, "MSYS2_ARG_CONV_EXCL": "*"}
vm, user, pwd = "kal", "kali", "kali"