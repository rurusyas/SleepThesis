# Orca — приложение для сна, стресса и концентрации

Мобильное приложение (iOS/Capacitor) + веб-демо + Telegram Mini App + Telegram-бот + FastAPI-бэкенд с моделью апноэ и AI-чатом.

## Что внутри

- `app/` — React + Vite + Capacitor (iOS, веб-демо, Telegram Mini App из одного кодбейза)
- `backend/` — FastAPI + SQLite, единый сервис для бота, Mini App и iOS
- `bot/` — Telegram-бот (python-telegram-bot)
- `apnea_model/` — сюда кладётся модель апноэ (интерфейс в README)
- `content/` — articles.json (10 научпоп-карточек с источниками), sounds.json
- `diagrams/` — 13 диаграмм Mermaid (.mmd) + экспорт в .svg
- `testing/` — план и результаты тестов

## 1. Веб-демо

```bash
cd app && npm i && npm run build:demo
```
Открыть `app/dist/` (или `npm run preview`). iPhone frame в CSS, навигация для презентации.

## 2. Приложение в браузере

```bash
cd app && npm i && npm run dev
```

## 3. iOS через Capacitor

```bash
cd app && npm i && npm run build && npx cap add ios && npx cap open ios
```
Нужен Xcode и Apple ID. Симулятор работает без платного аккаунта.

## 4. Бэкенд

Из корня репозитория:
```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```
Или `docker compose up backend`. Swagger: `http://localhost:8000/docs`.

## 5. Модель апноэ

Файлы — в `apnea_model/`. Интерфейс: `predict(audio_path: str) -> tuple[bool, float]`. Без модели бэкенд отдаёт заглушку (`used_model: false`). Подробно — `apnea_model/README.md`.

## 6. AI Chat

`backend/.env`: `LLM_API_KEY=sk-...` (Anthropic `ANTHROPIC_API_KEY` или OpenAI `OPENAI_API_KEY`). Без ключа — заглушка.

## 7. Telegram-бот

`@BotFather` -> `/newbot` -> токен в `bot/.env` -> `docker compose up bot`. Для Mini App: `/newapp`, указать URL деплоя.

## 8. Деплой

- Бэкенд: Railway / fly.io, `backend/Dockerfile`.
- Бот: Railway, папка `bot/`, env vars.
- Mini App / веб-демо: Vercel / Cloudflare Pages, `npm run build:telegram` / `build:demo`, папка `app/dist/`.

## 9. Тесты и диаграммы

```bash
make test       # pytest бэкенда + vitest фронта
make diagrams   # экспорт .mmd -> .svg через mermaid-cli
```

## Статус

Все компоненты собраны и протестированы.

| Компонент | Состояние |
|---|---|
| `backend/` | FastAPI + SQLite/Postgres, 8 эндпоинтов + `/health`, **14 pytest** ✓ |
| `apnea_model/` | VAD-эвристика по аудио (numpy + soundfile), proof-of-concept для демо; реальная SpO2-модель (UCDDB, ROC AUC 0.903) для iOS+HealthKit |
| `bot/` | python-telegram-bot, контракт с бэкендом проверен |
| `app/` веб | 8+ экранов: Onboarding, Home, Apnea, Diary, Sounds, Education, Chat, Focus, Profile, Routine и другие |
| `app/` Mini App | 6 экранов + упрощённый онбординг (4 шага), единый аккаунт по `tg_id` |
| `app/` тесты | **12 vitest** ✓ в `app/src/__tests__/` (indices, time, sse, sound) |
| `content/` | 10 статей с DOI, 8 звуков для Web Audio синтеза |
| `diagrams/` | 13 диаграмм Mermaid |
| `testing/` | план + результаты тестов (`testing/test_plan.md`, `testing/test_results.md`) |
| Деплой | `railway.toml` + `DEPLOY.md` (Railway для backend+bot, Cloudflare Pages для веб/Mini App) |

**Итого тестов: 26 / 26 зелёных** (14 backend + 12 frontend). См. [testing/test_results.md](testing/test_results.md).

### Команды

```bash
# backend
pytest backend/tests/

# frontend
cd app && npm test

# обе сборки
cd app && npm run build && npm run build:telegram
```
