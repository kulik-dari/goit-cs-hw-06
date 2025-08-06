# GoIT CS ДЗ-06 - Веб-застосунок з UDP Socket-сервером та MongoDB

Фінальне завдання курсу комп'ютерних систем: веб-застосунок без фреймворків з UDP сокетами та MongoDB.

## Структура проектуgoit-cs-hw-06/
├── main.py                 # HTTP та UDP сервери
├── Dockerfile              # Docker конфігурація
├── docker-compose.yaml     # Docker Compose
├── requirements.txt        # Залежності
├── front-init/            # HTML шаблони
│   ├── index.html
│   ├── message.html
│   ├── error.html
│   ├── style.css
│   ├── logo.png
│   └── storage/
└── README.md

## Технології

- Python 3.11 (без веб-фреймворків)
- HTTP Server + UDP Sockets
- MongoDB
- Docker & Docker Compose
- Multiprocessing

## Запуск

```bash
git clone <repo-url>
cd goit-cs-hw-06
docker compose up --build
Доступ: http://localhost:3000
Архітектура
HTTP-сервер (3000) → UDP Socket (5001) → MongoDB (27017)

Форма /message.html відправляє POST
HTTP-сервер передає дані через UDP
Socket-сервер зберігає в MongoDB
Редирект на головну

Перевірка даних
bashdocker exec -it goit-cs-hw-06-mongo-1 mongosh --eval "use messages_db; db.messages.find().pretty()"
Критерії виконання
✅ Один файл main.py з різними процесами
✅ Dockerfile та Docker контейнер
✅ docker-compose.yaml з MongoDB
✅ Docker Compose запуск
✅ Volumes для збереження даних
✅ Статичні ресурси (CSS, PNG)
✅ 404 error.html
✅ Форма → UDP → MongoDB
✅ Правильний формат документів MongoDB

