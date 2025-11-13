# Foodgram

Foodgram - это веб-приложение для публикации и обмена рецептами. Пользователи могут создавать рецепты, просматривать рецепты других пользователей, добавлять рецепты в избранное, подписываться на авторов, формировать список покупок и скачивать его в формате PDF.

## Технологии

- **Backend**: Python 3.11, Django 4.2.25, Django REST Framework 3.15.2, PostgreSQL 13.10
- **Frontend**: React, JavaScript
- **Инфраструктура**: Docker, Docker Compose, Nginx, Gunicorn
- **Дополнительно**: Djoser для аутентификации, Pillow для работы с изображениями, ReportLab для генерации PDF

## Установка и запуск

### Предварительные требования

- Установите Docker и Docker Compose на ваш компьютер.
- Клонируйте репозиторий:

```bash
git clone https://github.com/your-username/foodgram.git
cd foodgram
```

### Настройка переменных окружения

1. Создайте файл `.env` в корневой директории проекта на основе примера `.env.example`:

```bash
cp .env.example .env
```

2. Заполните переменные в `.env` файле:
   - `DB_ENGINE`: движок базы данных (django.db.backends.postgresql)
   - `DB_NAME`: имя базы данных
   - `DB_USER`: имя пользователя базы данных
   - `DB_PASSWORD`: пароль пользователя базы данных
   - `DB_HOST`: хост базы данных (db)
   - `DB_PORT`: порт базы данных (5432)
   - `SECRET_KEY`: секретный ключ Django
   - `DEBUG`: режим отладки (False для продакшена)
   - `ALLOWED_HOSTS`: разрешенные хосты

### Запуск приложения

1. Из корневой директории проекта выполните команду:

```bash
docker-compose up --build
```

Эта команда:
- Соберет и запустит контейнеры для базы данных (PostgreSQL), бэкенда (Django), фронтенда (React) и Nginx.
- Контейнер frontend подготовит статические файлы и завершит работу.
- Приложение будет доступно на порту 8000.

2. После успешного запуска выполните миграции и загрузите данные:

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py load_ingredients
```

### Доступ к приложению

- **Веб-приложение**: http://localhost
- **API документация**: http://localhost/api/docs/
- **Redoc**: http://localhost/api/redoc/

## API

API предоставляет следующие возможности:
- Регистрация и аутентификация пользователей
- Создание, чтение, обновление и удаление рецептов
- Добавление рецептов в избранное
- Подписка на авторов
- Формирование списка покупок
- Скачивание списка покупок в PDF

Полную спецификацию API можно найти по адресу http://localhost/api/docs/.

## Разработка

Для разработки локально без Docker:

1. Установите зависимости:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Настройте базу данных PostgreSQL локально или используйте Docker для БД.

3. Выполните миграции и запустите сервер:

```bash
python manage.py migrate
python manage.py runserver
```

4. Для фронтенда:

```bash
cd frontend
npm install
npm start
```

## Тестирование

Для запуска тестов:

```bash
docker-compose exec backend python manage.py test
```

## Деплой

Для продакшена используйте `docker-compose.production.yml`:

```bash
docker-compose -f docker-compose.production.yml up --build
```

