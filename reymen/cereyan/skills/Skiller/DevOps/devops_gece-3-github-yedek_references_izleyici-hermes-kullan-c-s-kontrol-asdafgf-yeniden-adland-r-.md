# Izleyici-Hermes kullanıcısı kontrolü (asdafgf yeniden adlandırıldı)
curl -s -o /dev/null -w "Izleyici-Hermes: %{http_code}\\n" https://api.github.com/users/Izleyici-Hermes
curl -s -o /dev/null -w "Watcher-Hermes: %{http_code}\\n" https://api.github.com/orgs/Watcher-Hermes