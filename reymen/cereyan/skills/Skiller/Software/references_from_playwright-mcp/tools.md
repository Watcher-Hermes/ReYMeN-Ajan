# Playwright MCP — Tam Araç Listesi

## Gezinme
- `browser_navigate(url)` — URL'ye git
- `browser_go_back()` — Geri git
- `browser_go_forward()` — İleri git
- `browser_reload()` — Sayfayı yenile

## Sayfa Okuma
- `browser_snapshot()` — Accessibility tree (metin tabanlı, token-verimli)
- `browser_take_screenshot(options?)` — Görsel ekran görüntüsü
- `browser_get_url()` — Mevcut URL
- `browser_title()` — Sayfa başlığı

## Etkileşim
- `browser_click(element, ref?)` — Elemana tıkla
- `browser_type(element, text)` — Metin yaz (karakter karakter)
- `browser_fill(element, value)` — Form alanını doğrudan doldur
- `browser_select_option(element, values)` — Dropdown seçim
- `browser_check(element)` / `browser_uncheck(element)` — Checkbox
- `browser_hover(element)` — Üzerine gel
- `browser_drag(startElement, endElement)` — Sürükle-bırak
- `browser_press_key(key)` — Klavye tuşu (Enter, Tab, Escape, vb.)
- `browser_upload_file(element, paths)` — Dosya yükle

## Bekleme
- `browser_wait_for(text?, textGone?, selector?, time?)` — Koşul bekle

## JavaScript
- `browser_evaluate(expression)` — JS kodu çalıştır, sonuç döner

## Ağ / Konsol
- `browser_network_requests()` — Tüm ağ isteklerini listele
- `browser_console_messages()` — Konsol mesajları (log/warn/error)

## Sekme / Pencere
- `browser_tab_list()` — Açık sekmeleri listele
- `browser_tab_new(url?)` — Yeni sekme aç
- `browser_tab_select(index)` — Sekmeye geç
- `browser_tab_close(index?)` — Sekme kapat

## Diğer
- `browser_close()` — Tarayıcı kapat
- `browser_save_as_pdf(filename?)` — PDF olarak kaydet (`--caps pdf` gerekli)
- `browser_generate_playwright_test()` — Playwright test kodu oluştur (`--codegen typescript`)
