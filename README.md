# River Connect

Интеллектуальная система связи для речных судов с ролями пассажир/экипаж, real-time мониторингом, уведомлениями и экстренной связью.

## Быстрый старт (Docker)

```bash
docker compose up --build
```

- **Frontend (React PWA):** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Локальная разработка

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# PostgreSQL и Redis должны быть запущены
python seed_data.py
uvicorn app.main:app --reload --port 8000
```

### Frontend React

```bash
cd frontend-react
npm install
npm run dev
```

### Frontend Vue

```bash
cd frontend-vue
npm install
npm run dev
```

## Тестовые аккаунты

| Роль | Email | Пароль | Каюта |
|------|-------|--------|-------|
| Пассажир | passenger1@test.com | password123 | A-101 |
| Пассажир | passenger2@test.com | password123 | B-205 |
| Капитан | captain@ship.com | captain123 | — |
| Экипаж | crew1@ship.com | crew123 | — |

## Функционал

### Пассажир
- Интерактивная карта с GPS, маршрутом и ETA
- Информация о судне и погоде
- Лента уведомлений с фильтрацией
- SOS-кнопка с подтверждением

### Экипаж
- Расширенная карта с техническими данными
- Панель управления уведомлениями
- Очередь SOS-запросов
- Массовые экстренные оповещения

## API Endpoints

- `POST /api/auth/login` — вход
- `GET /api/vessels/{id}` — данные судна
- `GET /api/notifications` — уведомления
- `POST /api/emergency` — SOS (пассажир)
- `WS /ws/vessels/{id}` — real-time телеметрия
- `WS /ws/notifications` — real-time уведомления
- `WS /ws/emergency` — real-time SOS

## Стек

- **Backend:** FastAPI, PostgreSQL, Redis, WebSocket, JWT
- **Frontend:** React + Vue (PWA), Leaflet, Tailwind CSS
