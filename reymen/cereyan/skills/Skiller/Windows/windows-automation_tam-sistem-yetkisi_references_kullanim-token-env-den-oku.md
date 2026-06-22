# Kullanim — token .env'den oku:
import os
from dotenv import load_dotenv
load_dotenv(r"C:\Users\marko\AppData\Local\hermes\.env")
test_telegram_bot(os.getenv("TELEGRAM_BOT_TOKEN", ""))
```

---