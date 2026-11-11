# AI Jobs Research

Информационная система для хранения и анализа данных о вакансиях в сфере искусственного интеллекта. Проект реализует REST API на Python/FastAPI, работу с PostgreSQL через SQLAlchemy, ETL-импорт из CSV, аналитику и простой веб-интерфейс.

## Предметная область и назначение

Система анализирует рынок труда в сфере ИИ на основе набора `Global AI Jobs 2026` (`data/global_ai_jobs_2026.csv`). Она хранит вакансии и связанные справочники (компании, страны/континенты, должности, специализации, отрасли, типы занятости, сертификации, навыки), позволяет управлять вакансиями, выполнять поиск/фильтрацию/сортировку, получать агрегированную аналитику и выполнять бизнес-операции сравнения и поиска похожих вакансий.

Подробное описание: [`docs/project_description.md`](docs/project_description.md).
ER-диаграмма: [`docs/erd.md`](docs/erd.md).

## Стек технологий

- Python 3.12
- FastAPI, Pydantic
- SQLAlchemy 2.x, PostgreSQL, psycopg
- Alembic (миграции)
- pytest, pytest-cov
- Docker, Docker Compose
- Frontend: HTML/CSS/JS (`frontend/static`)

## Структура проекта

```text
project/
├── src/ai_jobs/
│   ├── api/          # роутеры
│   ├── models/       # SQLAlchemy-модели
│   ├── schemas/      # Pydantic-схемы
│   ├── services/     # бизнес-логика
│   ├── etl/          # импорт и обработка данных
│   ├── core/         # конфигурация
│   ├── db/           # сессия БД, базовая модель, seed
│   └── main.py
├── migrations/       # Alembic-миграции
├── tests/            # unit и integration тесты
├── docs/             # описание и ERD
├── frontend/static/  # клиентский интерфейс
├── data/             # исходные CSV-данные
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

## Переменные окружения

Скопируйте `.env.example` в `.env` и при необходимости измените значения:

| Переменная | Назначение | Пример |
|---|---|---|
| `APP_NAME` | имя приложения | `AI Jobs Research` |
| `APP_ENV` | окружение | `development` |
| `DEBUG` | режим отладки | `true` |
| `DATABASE_URL` | строка подключения SQLAlchemy | `postgresql+psycopg://postgres:postgres@localhost:5432/ai_jobs_db` |
| `POSTGRES_DB` | имя БД (Postgres контейнер) | `ai_jobs_db` |
| `POSTGRES_USER` | пользователь БД | `postgres` |
| `POSTGRES_PASSWORD` | пароль БД | `postgres` |
| `POSTGRES_PORT` | порт БД на хосте | `5432` |
| `APP_PORT` | порт приложения | `8000` |
| `DATASET_PATH` | путь к CSV для ETL | `data/global_ai_jobs_2026.csv` |
| `LOG_LEVEL` | уровень логирования | `INFO` |

> В Docker Compose для сервиса `app` `DATABASE_URL` задаётся на хост `db` автоматически.

## Запуск через Docker (рекомендуется)

Требования: Docker и Docker Compose.

```bash
docker compose up --build
```

При старте контейнер `app`:
1. ожидает готовность PostgreSQL,
2. применяет миграции (`alembic upgrade head`),
3. выполняет seed демо-данных (`python -m ai_jobs.db.seed`, идемпотентно — пропускает, если вакансии уже есть),
4. запускает API на `http://localhost:8000`.

Интерфейс: `http://localhost:8000/`
Swagger/OpenAPI: `http://localhost:8000/docs`

Остановка: `docker compose down` (данные БД сохраняются в volume).

## Локальный запуск

Требования: Python 3.12, PostgreSQL, `uv` (или `pip`).

1. Установить зависимости:
```bash
uv sync
```
2. Поднять PostgreSQL (можно через Docker):
```bash
docker compose up -d db
```
3. Настроить `.env` (для локального запуска `DATABASE_URL` должен указывать на `localhost`).
4. Применить миграции:
```bash
uv run alembic upgrade head
```
5. (Опционально) наполнить БД демо-данными:
```bash
uv run python -m ai_jobs.db.seed
```
6. Запустить приложение:
```bash
uv run uvicorn ai_jobs.main:app --reload
```

## База данных, сущности и миграции

- Реляционная БД PostgreSQL, 11 таблиц: `continents`, `countries`, `companies`, `job_titles`, `specializations`, `industries`, `employment_types`, `certification_requirements`, `skills`, `vacancies`, `vacancy_skills`.
- Связи 1:N (география и справочники → вакансии) и M:N (вакансии ↔ навыки через `vacancy_skills`).
- Целостность: PK/FK, `UNIQUE`, `NOT NULL`, `CHECK` (диапазоны зарплат/процентов/рейтингов, даты, неотрицательные значения), индексы на FK и полях фильтрации.
- Схема управляется только миграциями Alembic (`migrations/versions/*`), миграции обратимы (`alembic downgrade -1`).
- ERD и описание сущностей: [`docs/erd.md`](docs/erd.md).

## Бизнес-правила (реализованы в сервисном слое `src/ai_jobs/services/`)

1. **Валидация и целостность вакансии (CRUD):** проверка существования связанных справочников и навыков, запрет дубликатов `source_job_id`, контроль диапазонов/дат и согласованности зарплат (`salary_min ≤ salary_usd ≤ salary_max`, дедлайн не раньше публикации) при создании/обновлении.
2. **Транзакционное создание/обновление вакансии со связями:** вакансия и её связи с навыками (`vacancy_skills`) сохраняются атомарно в рамках операции сервиса; при конфликте/ошибке транзакция откатывается.
3. **Поиск похожих вакансий (спец-операция):** подбор вакансий той же специализации по пересечению навыков с ранжированием по количеству совпавших навыков.
4. **Сравнение вакансий (спец-операция):** сравнение 2–5 выбранных вакансий с расчётом средней зарплаты, разницы между max/min и определением самой высоко- и низкооплачиваемой вакансии.
5. **Согласованная выдача списка:** пагинация, фильтрация, сортировка и поиск по списку вакансий с проверкой корректности параметров (например, `min_salary ≤ max_salary`).

## ETL-процесс

ETL импортирует данные из CSV в БД: **извлечение** (чтение строк с номерами строк) → **валидация и очистка** (Pydantic-валидация типов/форматов/диапазонов, пропуски и некорректные значения отклоняются) → **преобразование** (нормализация полей и навыков) → **загрузка** (upsert-подобная логика: существующие `source_job_id` пропускаются, справочники переиспользуются).

- Идемпотентность: повторный запуск не создаёт дубликатов (пропуск уже загруженных вакансий).
- Логирование: итог `total / loaded / skipped / rejected` и предупреждения по отклонённым строкам с причиной.

Запуск:
```bash
# локально
uv run python -m ai_jobs.etl.import_data --source data/global_ai_jobs_2026.csv

# в Docker (после запуска контейнеров)
docker compose exec app python -m ai_jobs.etl.import_data --source data/global_ai_jobs_2026.csv
```

Seed демо-данных (минимальный набор для проверки): `python -m ai_jobs.db.seed`.

## REST API

Базовый префикс: `/api/v1`. Документация: `/docs` (Swagger) и `/openapi.json`.

Основные эндпоинты:
- `GET /api/v1/vacancies` — список вакансий (пагинация `offset/limit`, фильтры, сортировка, поиск).
- `POST /api/v1/vacancies` — создание вакансии.
- `GET /api/v1/vacancies/{id}` — получение вакансии.
- `PATCH /api/v1/vacancies/{id}` — обновление вакансии.
- `DELETE /api/v1/vacancies/{id}` — удаление вакансии.
- `GET /api/v1/vacancies/{id}/similar` — похожие вакансии.
- `POST /api/v1/vacancies/compare` — сравнение вакансий.
- `GET /api/v1/analytics/summary`, `/salaries`, `/top-skills`, `/demand` — аналитика.
- `GET /api/v1/countries`, `/specializations`, `/skills`, `/industries`, `/companies`, `/job-titles`, `/employment-types`, `/certification-requirements` — справочники.

Единый формат ошибок: `{ "error": ..., "message": ..., "detail": ..., "details"?: ... }`.

### Примеры запросов

```bash
# список вакансий с фильтрацией и пагинацией
curl "http://localhost:8000/api/v1/vacancies?limit=10&min_salary=80000&sort_by=salary_usd&sort_order=desc"

# создание вакансии
curl -X POST "http://localhost:8000/api/v1/vacancies" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1, "country_id": 1, "job_title_id": 1,
    "specialization_id": 1, "industry_id": 1, "employment_type_id": 1,
    "experience_level": "Middle", "salary_usd": "90000.00",
    "skill_ids": [1, 2]
  }'

# сравнение вакансий
curl -X POST "http://localhost:8000/api/v1/vacancies/compare" \
  -H "Content-Type: application/json" \
  -d '{"vacancy_ids": [1, 2]}'

# аналитика: топ навыков
curl "http://localhost:8000/api/v1/analytics/top-skills?limit=10"
```

## Тестирование

```bash
# запуск тестов
uv run pytest

# тесты с покрытием (порог >= 70%)
uv run pytest --cov=ai_jobs --cov-report=term-missing --cov-fail-under=70
```

Тесты используют изолированную тестовую БД (SQLite in-memory) с созданием/удалением схемы на каждый тест и переопределением зависимости `get_db`.

### Отчёт о покрытии

![Отчёт о покрытии тестов](docs/coverage.png)

Покрытие кода соответствует требованию ТЗ (не менее 70%).


## CI

Workflow `.github/workflows/ci.yml` запускается на `push` и `pull_request`: установка зависимостей, `ruff format --check`, `ruff check`, `pytest` с покрытием (`--cov-fail-under=70`).

## Клиентский интерфейс

Веб-интерфейс (`/`) работает через API: просмотр списка вакансий с фильтрами, создание и редактирование, удаление, сравнение выбранных вакансий (ключевая бизнес-операция) и отображение ошибок пользователю.
