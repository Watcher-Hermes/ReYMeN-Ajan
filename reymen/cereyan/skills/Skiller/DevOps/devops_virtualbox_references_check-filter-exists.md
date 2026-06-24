# Check filter exists
VBoxManage showvminfo <vm-name> | grep -A 10 "USB Device Filters"