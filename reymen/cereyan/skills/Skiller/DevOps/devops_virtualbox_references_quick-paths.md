## Quick Paths

### 1. Check VM status
```bash
VBoxManage = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
subprocess.run([VBoxManage, "showvminfo", VM_NAME, "--machinereadable"])