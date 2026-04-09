# Hascelik Mail Automation Platform

Kurumsal e-posta otomasyonu için FastAPI + Celery + PostgreSQL + React tabanlı MVP iskeleti.

## Özellikler
- Microsoft Graph webhook/polling event alımı
- Queue tabanlı asenkron işleme
- Dil tespiti ve çeviri sağlayıcı soyutlamaları
- Config/database driven iş kuralı yönetimi
- Admin panel API + React yönetim ekranları
- Audit, webhook, gelen mail ve auto-reply logları
- Tüm API eylemlerinin merkezi audit log kaydı (istek method/path/status/duration)
- Tenant (firma) temel yönetimi: çoklu müşteri mimarisi için tenant kayıt/CRUD

## Kurulum
```bash
cp .env.example .env
docker compose up --build
```

## Backend
- FastAPI: `http://localhost:8000/docs`
- Health: `GET /health`

## Frontend
- React app: `http://localhost:5173`
- Admin panel login-first akışındadır (giriş yapılmadan diğer ekranlar açılmaz).

### Admin Login Yetkilendirme (Frontend)
Vite env değişkenleri:

- `VITE_ALLOWED_ADMIN_EMAILS=admin@hascelik.com,ops@hascelik.com`
- `VITE_ALLOWED_ADMIN_DOMAINS=hascelik.com`

Not:
- En az bir liste tanımlanabilir; tanımlı değilse varsayılan kullanıcı `admin@hascelik.com` olur.
- Domain bazlı giriş aktifleştirmek için `VITE_ALLOWED_ADMIN_DOMAINS` kullanılır.

### Employee User Yönetimi
- `Employee Users` ekranı sadece `admin` roldeki kullanıcıya açıktır.
- Employee kullanıcılar admin tarafından oluşturulur, güncellenir ve silinir.
- Employee kullanıcı oluştururken admin bir şifre belirler.
- Admin, employee kullanıcı için yeni şifre atayabilir (reset).
- Login sırasında admin olmayan kullanıcılar e-posta + şifre ile backend’de doğrulanır.

### Otomatik Yanıt Koruma Kuralları
- `mail_loop_guard_enabled=true`: Tanımlı/aktif mailbox kaynaklı gönderiler için otomatik cevap üretmez (mail loop engeli).
- `skip_if_thread_has_sent_reply=true`: Thread içinde Sent Items kaydı varsa (kullanıcı cevabı dahil) otomatik cevap üretmez.
- `language_detection_provider=mock|azure_translator`: Dil tespiti sağlayıcısını seçer.
- `translation_provider=mock|azure_translator`: Çeviri sağlayıcısını seçer.

### Microsoft Graph Webhook Notları
- Webhook endpoint: `POST /api/v1/webhooks/graph`
- Graph payload içindeki `resource` alanından `user` ve `message` id parse edilir.
- Mailbox eşlemesi önceliği:
1. Monitored mailbox `email`
2. Monitored mailbox `graph_user_id` (GUID/UPN)
- Opsiyonel güvenlik: `.env` üzerinde `GRAPH_WEBHOOK_CLIENT_STATE` tanımlanırsa gelen `clientState` bununla doğrulanır.

### Graph Subscription Yönetimi
- Admin API endpointleri:
1. `GET /api/v1/graph-subscriptions`
2. `POST /api/v1/graph-subscriptions/sync`
3. `POST /api/v1/graph-subscriptions/renew-due`
4. `POST /api/v1/graph-subscriptions/mailboxes/{mailbox_id}/subscribe`
5. `POST /api/v1/graph-subscriptions/mailboxes/{mailbox_id}/renew`
6. `DELETE /api/v1/graph-subscriptions/mailboxes/{mailbox_id}`
- Admin panelde `System > Graph Subscriptions` ekranından subscription yönetimi yapılabilir.
- Mailbox bazında resource otomatik `users/{graph_user_id or email}/messages` formatında oluşturulur.

### Multi-Tenant Foundation
- Admin API:
1. `GET /api/v1/tenants`
2. `POST /api/v1/tenants`
3. `PUT /api/v1/tenants/{tenant_id}`
4. `DELETE /api/v1/tenants/{tenant_id}`
- Admin panel: `System > Tenants`
- `X-Tenant-Code` header’ı API çağrılarında tenant context için kullanılabilir.
- Varsayılan tenant kodu: `.env` içindeki `DEFAULT_TENANT_CODE` (default: `default`)

Backend env:
- `ADMIN_USER_EMAILS=admin@hascelik.com,ops@hascelik.com`
- `ADMIN_USER_DOMAINS=hascelik.com`
- `GRAPH_WEBHOOK_NOTIFICATION_URL=https://admin.example.com/api/v1/webhooks/graph`
- `GRAPH_WEBHOOK_LIFECYCLE_URL=https://admin.example.com/api/v1/webhooks/lifecycle`
- `GRAPH_SUBSCRIPTION_EXPIRY_MINUTES=120`
- `GRAPH_SUBSCRIPTION_RENEW_THRESHOLD_MINUTES=30`
- `AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com`
- `AZURE_TRANSLATOR_KEY=<azure-translator-key>`
- `AZURE_TRANSLATOR_REGION=<azure-region>`
- `DEFAULT_TENANT_CODE=default`

### Gerçek Dil/Çeviri Sağlayıcısı Aktivasyonu
1. `.env` içine Azure Translator bilgilerini girin.
2. Admin panelde `Settings` ekranından aşağıdaki keyleri güncelleyin:
- `language_detection_provider=azure_translator`
- `translation_provider=azure_translator`
3. Worker servisini yeniden başlatın.

## Celery
- Worker: `backend.app.workers.celery_app.celery_app`

## Test
```bash
cd backend
pytest -q
```


## Frontend Screenshot Sistemi
Bu repoda browser tool olmadığında yerel/CI ortamında ekran görüntüsü üretmek için Playwright tabanlı bir script eklendi.

1. Frontend bağımlılıklarını kur:
```bash
cd frontend
npm install
npx playwright install chromium
```
2. Uygulama ayakta iken screenshot al:
```bash
npm run screenshot
```
3. Çıktılar:
- `frontend/screenshots/dashboard.png`
- `frontend/screenshots/mailbox-list.png`
- `frontend/screenshots/template-list.png`
- `frontend/screenshots/blocked-rules.png`

Opsiyonel env:
- `SCREENSHOT_BASE_URL` (varsayılan: `http://localhost:5173`)
- `SCREENSHOT_OUT_DIR` (varsayılan: `frontend/screenshots`)
