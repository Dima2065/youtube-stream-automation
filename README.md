# Автоматичне створення стріму на YouTube

Кожної суботи о **06:00 за Цюрихом** GitHub Actions автоматично створює
заплановану трансляцію на каналі «Українська Церква у Швейцарії»
зі стартом о **11:00** тієї ж суботи та обкладинкою з датою.

## Що в репозиторії

| Файл | Призначення |
|------|-------------|
| `create_stream.py` | основний скрипт: створює трансляцію + обкладинку |
| `get_token.py` | одноразове отримання токена (локально) |
| `background.jpg` | фон обкладинки (без дати) |
| `Montserrat.ttf` | шрифт дати (Thin / вага 100) |
| `requirements.txt` | залежності Python |
| `.github/workflows/create-stream.yml` | розклад запуску |

---

## Налаштування (один раз)

### 1. Google Cloud
1. Створіть проєкт на https://console.cloud.google.com
2. **APIs & Services → Library** → увімкніть **YouTube Data API v3**
3. **APIs & Services → OAuth consent screen** → заповніть, додайте себе у Test users,
   а потім **обов'язково натисніть Publish App** (статус має бути *In production*).
   Інакше токен помре через 7 днів.
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID →
   Application type: Desktop app** → завантажте `client_secret.json`.

### 2. Отримати токен (на своєму комп'ютері)
```bash
pip install google-auth-oauthlib
# покладіть client_secret.json поруч із get_token.py
python get_token.py
```
Відкриється браузер — увійдіть у Google-акаунт **каналу**. Скрипт виведе JSON.

### 3. Додати секрет у GitHub
Repository → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `YT_TOKEN`
- Secret: весь JSON з кроку 2 (одним рядком)

### 4. Готово
- Розклад спрацьовує щосуботи о 06:00 Zurich.
- Перевірити вручну: вкладка **Actions → Create YouTube Stream → Run workflow**.

---

## Як працює обкладинка
Скрипт бере `background.jpg` і малює дату найближчої суботи у форматі `ДД/ММ`
(шрифт Poppins Regular) у правому верхньому куті — так само, як у вашому дизайні.
Щоб змінити фон — просто замініть `background.jpg` (розмір 1280×720).

## Корисно знати
- Cron у GitHub Actions може запуститися із затримкою 5–15 хв — для створення
  стріму за 5 годин до ефіру це неважливо.
- GitHub вимикає розклад, якщо в репозиторії 60 днів немає активності.
  Раз на пару місяців запускайте workflow вручну або робіть коміт.
- Кожен запуск генерує НОВИЙ RTMP-ключ. Якщо у вас енкодер з постійним ключем —
  змініть `isReusable` на `True` у `create_stream.py`.

## Типографіка дати
- Шрифт: **Montserrat**, variable-файл `Montserrat.ttf`, вага по осі `FONT_WEIGHT_VALUE = 380` (товщина штриха ~21px).
- Розмір 120 px · Колір #000000 · без обведення/градієнта.
- Трекінг: **-70** (Canva), літери щільніше за замовчуванням.
- Тінь: rgba(0,0,0,30), зсув (2px, 2px), розмиття 5 px — ледь помітна.
- Згладжування: рендер у 4x із зменшенням (LANCZOS) для гладких кривих.
Усі значення — константи на початку `create_stream.py`. Щоб зробити трохи щільніше за вагою — `FONT_WEIGHT = "ExtraLight"`.
