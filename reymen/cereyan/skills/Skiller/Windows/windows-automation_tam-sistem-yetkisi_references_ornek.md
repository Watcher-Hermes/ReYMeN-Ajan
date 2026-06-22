# Ornek:
print(run_ps("Get-Process | Select-Object -First 5 Name, CPU"))
print(run_ps("netstat -an | Select-String '8080'"))
```

---