# Expected: {"connected": true/false}
   ```

6. Komut gönderme testi:
   ```bash
   curl -X POST http://localhost:5050/exec -H "Content-Type: application/json" -d '{"cmd":"whoami"}'