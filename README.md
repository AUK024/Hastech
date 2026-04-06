# Hascelik Mail Automation Platform

Kurumsal e-posta otomasyonu için FastAPI + Celery + PostgreSQL + React tabanlı MVP iskeleti.

## Özellikler
- Microsoft Graph webhook/polling event alımı
- Queue tabanlı asenkron işleme
- Dil tespiti ve çeviri sağlayıcı soyutlamaları
- Config/database driven iş kuralı yönetimi
- Admin panel API + React yönetim ekranları
- Audit, webhook, gelen mail ve auto-reply logları

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
