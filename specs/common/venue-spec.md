# 📋 Техническая Спецификация Реализации
## Venue Service

**Версия документа:** 1.0.0  
**Дата:** 2026-03-16  
**Статус:** Утверждено для реализации  
**Язык реализации:** Python 3.12+  
**Package Manager:** uv

---

## 1. Обзор и Назначение Документа

### 1.1. Цель Документа
Данный документ определяет полную техническую спецификацию для реализации **Venue Service** — сервиса управления компаниями, заведениями и выплатами в платформе реализации излишков продукции. Спецификация предназначена для команды разработки и содержит исчерпывающие требования к архитектуре, структуре проекта, компонентам, интеграциям и процессам.

### 1.2. Область Применения
Спецификация охватывает:
- ✅ Структуру проекта и организацию кода
- ✅ Технологический стек и зависимости
- ✅ Слои архитектуры (API, Business, Data)
- ✅ Интеграции (Gateway, RabbitMQ, PostgreSQL, gRPC)
- ✅ Безопасность и аутентификацию
- ✅ Логирование и наблюдаемость
- ✅ Тестирование и деплой

### 1.3. Контекст Архитектуры

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Platform Architecture                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────────────────┐ │
│  │   Client     │────▶│   Gateway    │────▶│    Venue Service        │ │
│  │  (Mobile/    │     │   (Kong)     │     │    (Python/FastAPI)     │ │
│  │   Web)       │     │              │     │                         │ │
│  └──────────────┘     └──────────────┘     └───────────┬─────────────┘ │
│                                                         │               │
│                              ┌──────────────────────────┼──────────────┤
│                              │                          │              │
│                              ▼                          ▼              ▼
│                       ┌──────────────┐          ┌──────────────┐ ┌──────────┐
│                       │  PostgreSQL  │          │   RabbitMQ   │ │  Auth    │
│                       │  (db_venue)  │          │   (Events)   │ │  (gRPC)  │
│                       └──────────────┘          └──────────────┘ └──────────┘
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Ключевые принципы:**
- **Database Per Service** — Venue Service владеет `db_venue`
- **Event-Driven** — Публикация событий в RabbitMQ для других сервисов
- **Identity Propagation** — Заголовки идентичности от API Gateway
- **Soft Delete** — `deleted_at` вместо физического удаления
- **Audit Logging** — Все mutating операции логируются

---

## 2. Технологический Стек

### 2.1. Основные Технологии

| Компонент | Технология | Версия | Обоснование |
|-----------|------------|--------|-------------|
| Язык | Python | 3.12+ | Типизация, производительность, экосистема |
| Package Manager | uv | 0.5+ | Быстрая установка зависимостей, lock-файлы |
| Web Framework | FastAPI | 0.115+ | Автоматическая OpenAPI, асинхронность, валидация |
| ORM | SQLAlchemy | 2.0+ | Async support, типизация, миграции |
| Migrations | Alembic | 1.13+ | Версионирование схемы БД |
| Validation | Pydantic | 2.9+ | Валидация данных, сериализация |
| Message Broker | RabbitMQ | 3.12+ | Event streaming, асинхронная коммуникация |
| AMQP Client | aio-pika | 9.4+ | Асинхронный клиент для RabbitMQ |
| Cache | Redis | 7.2+ | Кэширование, rate limiting |
| Redis Client | redis-py | 5.0+ | Async support |
| gRPC Client | grpcio | 1.60+ | Межсервисное взаимодействие |
| Security | python-jose | 3.3+ | JWT обработка (для отладки) |

### 2.2. Зависимости (pyproject.toml)

```toml
[project]
name = "venue-service"
version = "1.0.0"
description = "Venue Management Service for Surplus Food Platform"
requires-python = ">=3.12"

[project.dependencies]
# Web Framework
fastapi = "^0.115.0"
uvicorn = {version = "^0.32.0", extras = ["standard"]}

# Database
sqlalchemy = {version = "^2.0.35", extras = ["asyncio"]}
asyncpg = "^0.30.0"
alembic = "^1.13.0"

# Validation
pydantic = "^2.9.0"
pydantic-settings = "^2.6.0"

# Message Broker
aio-pika = "^9.4.0"

# Cache
redis = {version = "^5.0.0", extras = ["hiredis"]}

# gRPC
grpcio = "^1.60.0"
grpcio-tools = "^1.60.0"

# Security
python-jose = {version = "^3.3.0", extras = ["cryptography"]}

# Observability
structlog = "^24.4.0"
opentelemetry-api = "^1.27.0"
opentelemetry-sdk = "^1.27.0"
opentelemetry-instrumentation-fastapi = "^0.48b0"
opentelemetry-exporter-otlp = "^1.27.0"
prometheus-client = "^0.21.0"

# Utilities
python-multipart = "^0.0.12"
httpx = "^0.27.0"
tenacity = "^9.0.0"
decimal = "^0.1.0"

[tool.uv]
dev-dependencies = [
    "pytest = "^8.3.0",
    "pytest-asyncio = "^0.24.0",
    "pytest-cov = "^6.0.0",
    "httpx = "^0.27.0",
    "factory-boy = "^3.3.0",
    "ruff = "^0.7.0",
    "mypy = "^1.12.0",
]
```

### 2.3. Инструменты Разработки

| Инструмент | Назначение | Конфигурация |
|------------|------------|--------------|
| uv | Управление зависимостями | uv.lock |
| ruff | Linting | ruff.toml |
| mypy | Static type checking | mypy.ini |
| pytest | Тестирование | pytest.ini |
| pre-commit | Git hooks | .pre-commit-config.yaml |

---

## 3. Структура Проекта

### 3.1. Directory Layout

```
venue-service/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # CI pipeline
│       └── cd.yml                    # CD pipeline
├── .venv/                             # Virtual environment (uv)
├── alembic/
│   ├── versions/                     # Migration files
│   ├── env.py                        # Alembic environment
│   └── script.py.mako                # Migration template
├── src/
│   ├── __init__.py
│   ├── main.py                       # Application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py               # Configuration management
│   │   └── logging.py                # Logging configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                   # Dependencies (DI)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── companies.py
│   │   │   ├── venues.py
│   │   │   ├── payouts.py
│   │   │   └── health.py
│   │   └── v1/
│   │       └── router.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                   # Base model class
│   │   ├── company.py
│   │   ├── venue.py
│   │   └── payout.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py                 # Common schemas (pagination, error)
│   │   ├── company.py
│   │   ├── venue.py
│   │   └── payout.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── company_service.py
│   │   ├── venue_service.py
│   │   ├── payout_service.py
│   │   └── event_publisher.py        # RabbitMQ event publishing
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                   # Base repository
│   │   ├── company_repository.py
│   │   ├── venue_repository.py
│   │   └── payout_repository.py
│   ├── grpc/
│   │   ├── __init__.py
│   │   ├── client.py                 # gRPC client for Auth service
│   │   └── protos/                   # Generated protobuf files
│   ├── events/
│   │   ├── __init__.py
│   │   ├── publisher.py              # RabbitMQ event publisher
│   │   ├── schemas.py                # Event schemas
│   │   └── topics.py                 # RabbitMQ exchange/routing keys
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py                   # Identity headers validation
│   │   ├── logging.py                # Request/Response logging
│   │   ├── tracing.py                # OpenTelemetry integration
│   │   └── error_handler.py          # Global exception handling
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── pagination.py
│   │   ├── security.py
│   │   ├── validators.py
│   │   └── geo.py                    # Geo calculations (Haversine)
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── unit/
│       ├── integration/
│       └── e2e/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── migrate.sh
│   └── seed.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── README.md
└── Makefile
```

### 3.2. Описание Ключевых Директорий

| Директория | Назначение | Ответственность |
|------------|------------|-----------------|
| `src/` | Исходный код сервиса | Вся бизнес-логика |
| `api/routes/` | HTTP endpoints | Маршрутизация запросов |
| `models/` | SQLAlchemy модели | ORM mapping к БД |
| `schemas/` | Pydantic схемы | Валидация request/response |
| `services/` | Business logic | Use cases, orchestration |
| `repositories/` | Data access | CRUD операции с БД |
| `events/` | Event publishing | RabbitMQ integration |
| `grpc/` | gRPC client | Межсервисное взаимодействие |
| `middleware/` | Cross-cutting concerns | Auth, logging, tracing |
| `config/` | Configuration | Settings, environment |
| `tests/` | Test suites | Unit, integration, e2e |

---

## 4. Конфигурация и Настройки

### 4.1. Environment Variables

```bash
# Application
APP_NAME=venue-service
APP_VERSION=1.0.0
APP_ENV=production  # development, staging, production
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8002
WORKERS=4
RELOAD=false

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db_venue
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30

# RabbitMQ
RABBITMQ_URL=amqp://user:password@rabbitmq:5672/
RABBITMQ_EVENT_EXCHANGE=venue.events
RABBITMQ_PRODUCER_CONFIRM=true

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=300

# gRPC (Auth Service)
AUTH_SERVICE_HOST=auth-service
AUTH_SERVICE_PORT=50051
AUTH_SERVICE_TIMEOUT=5.0

# Observability
OTEL_SERVICE_NAME=venue-service
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security (from Gateway)
GATEWAY_TRUSTED_NETWORKS=10.0.0.0/8,172.16.0.0/12
```

### 4.2. Settings Management (src/config/settings.py)

**Задачи:**
- Централизованное управление конфигурацией
- Валидация переменных окружения при старте
- Поддержка разных окружений (dev/staging/prod)
- Type-safe configuration через Pydantic Settings

**Требования:**
- Использовать `pydantic-settings` для загрузки из .env
- Валидировать все обязательные переменные при инициализации
- Поддерживать hot-reload для development режима
- Шифровать чувствительные данные (DATABASE_URL, etc.)

### 4.3. Logging Configuration (src/config/logging.py)

**Задачи:**
- Структурированное логирование (JSON format)
- Correlation ID (X-Request-ID) в каждом логе
- Интеграция с OpenTelemetry для tracing
- Разные уровни логирования для разных окружений

**Формат Лога:**
```json
{
   "timestamp": "2026-03-16T10:30:00.000Z",
   "level": "INFO",
   "service": "venue-service",
   "trace_id": "0-abc123def456",
   "span_id": "abc123",
   "request_id": "uuid-here",
   "user_id": "uuid-here",
   "action": "venue.created",
   "message": "Venue created successfully",
   "duration_ms": 45
}
```

---

## 5. Слои Архитектуры

### 5.1. Архитектурные Слои

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           API Layer (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Routes / Controllers                                           │   │
│  │  - HTTP request/response handling                               │   │
│  │  - Input validation (Pydantic)                                  │   │
│  │  - Authentication (Gateway headers)                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                        Service Layer (Business Logic)                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Services / Use Cases                                           │   │
│  │  - Business rules enforcement                                   │   │
│  │  - Transaction management                                       │   │
│  │  - Event publishing                                             │   │
│  │  - Cross-repository orchestration                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                       Repository Layer (Data Access)                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Repositories                                                   │   │
│  │  - CRUD operations                                              │   │
│  │  - Query building                                               │   │
│  │  - Soft delete handling                                         │   │
│  │  - Pagination                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                          Infrastructure Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │
│  │   PostgreSQL    │  │    RabbitMQ     │  │       Redis         │   │
│  │   (db_venue)    │  │   (Events)      │  │     (Cache)         │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2. API Layer

**Файл:** `src/api/v1/router.py`

**Задачи:**
- Регистрация всех route handlers
- Версионирование API (`/api/v1/`)
- Middleware подключение
- OpenAPI documentation generation

**Требования:**
- Все routes префиксированы `/api/v1/`
- Каждый route имеет tags для Swagger UI
- Response models строго типизированы
- Error responses стандартизированы

**Файл:** `src/api/deps.py`

**Задачи:**
- Dependency injection для FastAPI
- Извлечение identity headers от Gateway
- Валидация обязательных заголовков
- Предоставление context для services

**Извлекаемые Заголовки:**

| Заголовок | Тип | Обязательный | Описание |
|-----------|-----|-------------|----------|
| X-User-ID | string | ✅ | ID пользователя из auth_db |
| X-User-Role | Enum | ✅ | Роль (user/staff/admin) |
| X-User-Venue-ID | string | ⚠️ | ID заведения для роли staff |
| X-Request-ID | string | ✅ | Correlation ID для tracing |

### 5.3. Service Layer

**Назначение:** Бизнес-логика и orchestration

**Принципы:**
- **Single Responsibility** — Один service = один aggregate root
- **Transaction Management** — Все mutating операции в транзакции
- **Event Publishing** — Публикация событий после успешной транзакции
- **No Direct DB Access** — Только через repositories

**Интерфейсы Service:**

```
Interface CompanyService:
  - get_by_id(company_id: int) -> Company
  - list(filters, pagination) -> PaginatedResult[Company]
  - create(data: CompanyCreate, context: IdentityContext) -> Company
  - update(company_id: int, data: CompanyUpdate, context: IdentityContext) -> Company
  - soft_delete(company_id: int, context: IdentityContext) -> None

Interface VenueService:
  - get_by_id(venue_id: int) -> Venue
  - list(filters, pagination, geo_params) -> PaginatedResult[Venue]
  - create(data: VenueCreate, context: IdentityContext) -> Venue
  - update(venue_id: int, data: VenueUpdate, context: IdentityContext) -> Venue
  - soft_delete(venue_id: int, context: IdentityContext) -> None
  - search_by_name(name: str, filters) -> List[Venue]
  - search_by_geo(lat, lon, radius) -> List[Venue]

Interface PayoutService:
  - get_by_id(payout_id: int) -> Payout
  - list_by_venue(venue_id: int, filters) -> List[Payout]
  - create(data: PayoutRequest, venue_id: int, context: IdentityContext) -> Payout
  - update_status(payout_id: int, status: str, context: IdentityContext) -> None
```

### 5.4. Repository Layer

**Назначение:** Data access abstraction

**Принципы:**
- **One Repository per Aggregate** — CompanyRepository, VenueRepository, PayoutRepository
- **Base Repository** — Общие CRUD операции в базовом классе
- **Soft Delete** — Все queries фильтруют `deleted_at IS NULL`
- **Async Only** — Все методы асинхронные

**Базовый Интерфейс:**
```
Interface BaseRepository[T]:
  - get_by_id(id: int) -> Optional[T]
  - list(filters, pagination) -> Sequence[T]
  - count(filters) -> int
  - create(data) -> T
  - update(id: int, data) -> T
  - soft_delete(id: int) -> None
  - hard_delete(id: int) -> None  # Только для cleanup jobs
```

**Специфичные Методы:**

| Repository | Специфичные Методы |
|------------|-------------------|
| VenueRepository | search_by_name(name), search_by_geo(lat, lon, radius), find_by_company(company_id) |
| PayoutRepository | list_by_venue(venue_id, status), find_pending_by_venue(venue_id) |
| CompanyRepository | find_by_inn(inn), list_active() |

### 5.5. Event Publishing Layer

**Назначение:** Публикация domain events в RabbitMQ

**Важно:** Venue Service НЕ отправляет уведомления напрямую. Вместо этого публикует события, которые потребляет Notification Service и другие сервисы.

**Файл:** `src/events/publisher.py`

**Задачи:**
- Асинхронная публикация событий в RabbitMQ
- Retry logic при временных ошибках broker
- Schema validation перед публикацией
- Correlation ID propagation

**Файл:** `src/events/topics.py`

**RabbitMQ Exchanges/Routing Keys:**

| Exchange | Routing Key | Описание | Producer | Consumers |
|----------|-------------|----------|----------|-----------|
| venue.events | venue.created | Создание заведения | Venue | Notification, Catalog |
| venue.events | venue.updated | Обновление заведения | Venue | Notification, Catalog |
| venue.events | venue.deleted | Удаление заведения | Venue | Notification, Catalog |
| payout.events | payout.created | Создание заявки на выплату | Venue | Payment, Notification |
| payout.events | payout.paid | Выплата выполнена | Venue | Payment, Notification |

**Файл:** `src/events/schemas.py`

**Event Schema:**
```json
{
   "event_id": "uuid",
   "event_type": "venue.created",
   "timestamp": "2026-03-16T10:30:00Z",
   "aggregate_id": "venue_id",
   "aggregate_type": "Venue",
   "payload": {
     "venue_id": 123,
     "company_id": 456,
     "name": "Burger King",
     "address": "Moscow, st. Lenin 1",
     "latitude": 55.7558,
     "longitude": 37.6173
   },
   "metadata": {
     "service_origin": "venue-service",
     "trace_id": "opentelemetry-trace-id",
     "correlation_id": "request-uuid",
     "user_id": "uuid"
   }
}
```

---

## 6. Модели Данных

### 6.1. SQLAlchemy Models

**Файл:** `src/models/base.py`

**Базовый Класс:**
- Все модели наследуются от `Base`
- Автоматические поля: `id`, `created_at`, `updated_at`
- Soft delete support: `deleted_at`
- Async session support

**Модели (соответствуют venue.sql):**

| Модель | Таблица | Ключевые Поля | Soft Delete |
|--------|---------|---------------|-------------|
| Company | venue.companies | id, name, inn, is_active | deleted_at |
| Venue | venue.venues | id, company_id, name, address, lat, lon, commission_rate, payout_balance | deleted_at |
| Payout | venue.payouts | id, venue_id, amount, period_start, period_end, status | Нет |

**Важные Заметки:**
- `company_id` — FK к venue.companies (ON DELETE SET NULL)
- `venue_id` в payouts — FK к venue.venues (ON DELETE RESTRICT)
- JSONB поля: `work_schedule`, `payment_details`
- DECIMAL поля для денег: `commission_rate`, `payout_balance`, `amount`

### 6.2. Pydantic Schemas

**Файл:** `src/schemas/common.py`

**Общие Схемы:**
- `PaginatedResponse[T]` — Универсальный пагинированный ответ
- `PaginationMeta` — Метаданные пагинации
- `ErrorResponse` — Стандартизированный формат ошибок
- `IdentityContext` — Контекст идентичности от Gateway

**Схемы по Доменам:**
- Company, CompanyCreate, CompanyUpdate
- Venue, VenueCreate, VenueUpdate
- Payout, PayoutRequest
- Enums: UserRole, PayoutStatus

**Требования:**
- Все схемы с явной типизацией
- Validation rules (max_length, format, enum)
- Separate schemas for Create/Update/Response
- Config для serialization (exclude_unset, etc.)
- Decimal поля для денег (не float)

---

## 7. Безопасность и Аутентификация

### 7.1. Authentication Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │────▶│   Gateway    │────▶│ Venue Service│
│              │     │    (Kong)    │     │  (Python)    │
└──────────────┘     └──────────────┘     └──────────────┘
      │                    │                    │
      │ 1. JWT Token       │                    │
      │───────────────────▶│                    │
      │                    │                    │
      │                    │ 2. Validate JWT    │
      │                    │ 3. Extract Claims  │
      │                    │                    │
      │                    │ 4. Add Headers     │
      │                    │───────────────────▶│
      │                    │  X-User-ID         │
      │                    │  X-User-Role       │
      │                    │  X-Request-ID      │
      │                    │                    │
      │                    │                    │ 5. Trust Headers
      │                    │                    │ (from trusted network)
```

### 7.2. Middleware: Auth (src/middleware/auth.py)

**Задачи:**
- Валидация наличия обязательных identity headers
- Проверка доверенной сети (Gateway only)
- Извлечение контекста для request scope
- Блокировка прямых запросов без Gateway

**Требования:**
- Отклонять запросы без `X-User-ID`, `X-Request-ID`
- Проверять IP адрес против `GATEWAY_TRUSTED_NETWORKS`
- Логировать все auth failures
- Возвращать стандартизированные 401/403 ошибки

### 7.3. Authorization Rules

| Resource | Action | user | staff | admin |
|----------|--------|------|-------|-------|
| companies | GET (list) | ❌ | ❌ | ✅ |
| companies | CREATE | ❌ | ❌ | ✅ |
| companies | UPDATE | ❌ | ❌ | ✅ |
| companies | DELETE | ❌ | ❌ | ✅ |
| venues | GET (list) | ✅ | ✅ | ✅ |
| venues | GET (single) | ✅ | ✅ | ✅ |
| venues | CREATE | ❌ | ✅* | ✅ |
| venues | UPDATE | ❌ | ✅* | ✅ |
| venues | DELETE | ❌ | ❌ | ✅ |
| payouts | GET (list) | ❌ | ✅* | ✅ |
| payouts | CREATE | ❌ | ❌ | ✅ |

\* — staff имеет доступ только к своим заведениям (по X-User-Venue-ID)

### 7.4. Audit Logging

**Файл:** `src/middleware/logging.py`

**Требования:**
- Логировать все mutating операции (POST/PUT/PATCH/DELETE)
- Записывать old_values и new_values для чувствительных данных
- Включать X-User-ID, X-Request-ID, X-Forwarded-For в каждый лог
- Структурированный JSON формат для SIEM интеграции

**Audit Log Entry:**
```json
{
   "timestamp": "2026-03-16T10:30:00Z",
   "event_type": "audit.record_updated",
   "user_id": "uuid",
   "action": "UPDATE",
   "resource_type": "Venue",
   "resource_id": "123",
   "old_values": {"commission_rate": "10.00"},
   "new_values": {"commission_rate": "12.00"},
   "ip_address": "192.168.1.100",
   "request_id": "uuid",
   "trace_id": "opentelemetry-trace-id"
}
```

---

## 8. Observability

### 8.1. Logging

**Библиотека:** structlog

**Конфигурация:**
- Development: Console output, pretty format
- Production: JSON format, stdout
- Log levels: DEBUG (dev), INFO (staging), WARNING (prod)

**Структура Лога:**
```json
{
   "timestamp": "ISO8601",
   "level": "INFO|WARNING|ERROR",
   "service": "venue-service",
   "version": "1.0.0",
   "trace_id": "string",
   "span_id": "string",
   "request_id": "uuid",
   "user_id": "uuid",
   "action": "string",
   "resource": "string",
   "duration_ms": "integer",
   "message": "string"
}
```

### 8.2. Distributed Tracing

**Стандарт:** OpenTelemetry

**Интеграция:**
- FastAPI instrumentation (auto)
- SQLAlchemy instrumentation (manual)
- RabbitMQ instrumentation (manual)
- Redis instrumentation (auto)
- Exporter: OTLP → Jaeger/Tempo

**Spans:**
- HTTP Request span (root)
- Service method span
- Repository query span
- RabbitMQ publish span
- gRPC call span (Auth service)

### 8.3. Metrics

**Библиотека:** prometheus-client

**Метрики:**

| Метрика | Тип | Описание |
|--------|-----|---------|
| http_requests_total | Counter | Количество HTTP запросов |
| http_request_duration_seconds | Histogram | Латентность запросов |
| db_query_duration_seconds | Histogram | Время выполнения запросов к БД |
| rabbitmq_events_published_total | Counter | Количество опубликованных событий |
| active_db_connections | Gauge | Активные соединения к БД |
| cache_hits_total | Counter | Cache hits |
| cache_misses_total | Counter | Cache misses |

**Endpoints:**
- `/metrics` — Prometheus scrape endpoint
- `/health` — Liveness probe
- `/ready` — Readiness probe

---

## 9. Обработка Ошибок

### 9.1. Error Response Format

**Файл:** `src/schemas/common.py`

```json
{
   "code": "VALIDATION_ERROR",
   "message": "Неверные данные в запросе",
   "details": [
     {"field": "name", "message": "Поле обязательно для заполнения"}
   ],
   "timestamp": "2026-03-16T10:30:00Z",
   "request_id": "uuid",
   "trace_id": "string"
}
```

### 9.2. Error Codes

| Code | HTTP Status | Описание |
|------|-------------|----------|
| VALIDATION_ERROR | 400 | Ошибка валидации входных данных |
| UNAUTHORIZED | 401 | Требуется аутентификация |
| FORBIDDEN | 403 | Недостаточно прав |
| NOT_FOUND | 404 | Ресурс не найден |
| CONFLICT | 409 | Конфликт (дубликат, etc.) |
| INTERNAL_ERROR | 500 | Внутренняя ошибка сервера |
| SERVICE_UNAVAILABLE | 503 | Сервис недоступен |

### 9.3. Global Exception Handler

**Файл:** `src/middleware/error_handler.py`

**Задачи:**
- Перехват всех необработанных исключений
- Логирование с trace_id
- Возврат стандартизированного error response
- Не раскрытие внутренней информации в production

---

## 10. Интеграции с Другими Сервисами

### 10.1. gRPC Взаимодействие (Синхронное)

| Сервис | Направление | Протокол | Цель |
|--------|-------------|----------|------|
| Auth | ← Входящий | gRPC | Валидация venue_id для staff_profiles |
| Catalog | ← Входящий | gRPC | Проверка существования venue_id для офферов |
| Order | ← Входящий | gRPC | Проверка существования venue_id для заказов |

**gRPC Контракты (логический уровень):**

| Метод | Вход | Выход | Описание |
|-------|------|-------|----------|
| GetVenueById | venue_id: int64 | name, address, is_open, commission_rate | Проверка заведения |
| GetVenueCoordinates | venue_id: int64 | latitude, longitude | Для карты в приложении |
| UpdatePayoutBalance | venue_id, amount | success, new_balance | Начисление после заказа |

### 10.2. RabbitMQ Взаимодействие (Асинхронное)

| Событие | Публикует | Подписчики | Действие |
|---------|-----------|------------|----------|
| venue.created | Venue | Notification, Catalog | Уведомление, индексация |
| venue.updated | Venue | Notification, Catalog | Обновление кэша |
| venue.deleted | Venue | Notification, Catalog | Удаление из индекса |
| payout.created | Venue | Payment, Notification | Обработка выплаты |
| payout.paid | Venue | Payment, Notification | Подтверждение выплаты |

---

## 11. Тестирование

### 11.1. Test Strategy

| Уровень | Инструмент | Coverage Target | Описание |
|---------|------------|-----------------|----------|
| Unit | pytest | 80%+ | Тестирование отдельных функций |
| Integration | pytest + TestContainers | 70%+ | Тестирование с БД, RabbitMQ |
| E2E | pytest + httpx | 60%+ | Сквозные сценарии API |
| Contract | pytest | 100% | OpenAPI spec validation |

### 11.2. Test Structure

```
src/venue_service/tests/
├── conftest.py              # Fixtures, test config
├── unit/
│   ├── test_services/
│   ├── test_repositories/
│   └── test_utils/
├── integration/
│   ├── test_companies_api/
│   ├── test_venues_api/
│   ├── test_payouts_api/
│   └── test_events/
└── e2e/
    ├── test_venue_crud_flow/
    ├── test_payout_flow/
    └── test_geo_search/
```

### 11.3. Test Fixtures

**conftest.py:**
- `async_client` — Async HTTP client for API tests
- `db_session` — Isolated DB session per test
- `rabbitmq_mock` — Mock for RabbitMQ publisher
- `identity_context` — Test identity headers
- `factory_boy` — Factories для создания тестовых данных

### 11.4. CI Pipeline (.github/workflows/ci.yml)

**Stages:**
1. Lint — ruff, mypy
2. Test — pytest with coverage
3. Build — Docker image build
4. Security — Dependency scan (safety, pip-audit)

**Requirements:**
- Все PR требуют passing CI
- Coverage не должен уменьшаться
- Security vulnerabilities блокируют merge

---

## 12. Миграции Базы Данных

### 12.1. Alembic Configuration

**Файл:** `alembic/env.py`

**Настройки:**
- Async support для PostgreSQL
- Target metadata из models/base.py
- Transaction per migration
- Schema: venue

### 12.2. Migration Workflow

```bash
# Create new migration
alembic revision --autogenerate -m "add_venue_phone_field"

# Review and edit migration file
# Apply to database
alembic upgrade head

# Rollback
alembic downgrade -1
```

### 12.3. Migration Rules

- Never edit committed migration files
- Always test migrations on staging before production
- Backward compatible — не ломать существующий API
- Data migrations — отдельный тип миграций с data backup
- Использовать существующую схему venue.sql как baseline

---

## 13. Деплой и Инфраструктура

### 13.1. Docker Configuration

**Файл:** `docker/Dockerfile`

**Требования:**
- Multi-stage build (build → runtime)
- Non-root user для безопасности
- Health check endpoint
- Graceful shutdown support

**Image Layers:**
1. Python base image (slim)
2. uv install
3. Dependencies install
4. Source code copy
5. Non-root user

### 13.2. Kubernetes Deployment

**Resources:**
- Deployment (replicas: 3 min)
- Service (ClusterIP)
- HorizontalPodAutoscaler (CPU/Memory)
- PodDisruptionBudget

**Probes:**
- Liveness: `/health` (30s interval)
- Readiness: `/ready` (10s interval)
- Startup: `/health` (initial delay 30s)

### 13.3. Environment Configuration

| Environment | Replicas | Resources | Database | RabbitMQ |
|-------------|----------|-----------|----------|----------|
| Development | 1 | 256Mi/100m | Local Docker | Local Docker |
| Staging | 2 | 512Mi/250m | Managed PostgreSQL | Managed RabbitMQ |
| Production | 3+ | 1Gi/500m | Managed PostgreSQL | Managed RabbitMQ |

### 13.4. CI/CD Pipeline

**Stages:**
1. Build — Docker image, push to registry
2. Test — Run test suite on staging
3. Deploy Staging — Automatic on merge to main
4. Deploy Production — Manual approval required

**Rollback Strategy:**
- Kubernetes rollout undo
- Database migration rollback plan
- Feature flags для gradual rollout

---

## 14. Производительность и Масштабирование

### 14.1. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (P95) | ≤ 1000ms | Prometheus histogram |
| Database Query Time (P95) | ≤ 200ms | SQLAlchemy logging |
| RabbitMQ Publish Latency | ≤ 50ms | Producer callback |
| Error Rate | ≤ 0.1% | Error logs / total requests |

### 14.2. Caching Strategy

**Redis Usage:**

| Key Pattern | TTL | Purpose |
|------------|-----|---------|
| venue:{id} | 5min | Venue profile cache |
| company:{id} | 5min | Company profile cache |
| geo:venues:{lat}:{lon}:{radius} | 1min | Geo search results |
| venue:open_status:{id} | 1min | Open/closed status |

**Cache Invalidation:**
- На invalidated после mutating операций
- Event-driven invalidation через RabbitMQ
- Time-based expiration для geo queries

### 14.3. Database Optimization

**Indexes (из venue.sql):**
- Все foreign keys indexed (`venues_idx_company`, `payouts_idx_venue`)
- Location index (`venues_idx_location` на latitude, longitude)
- Open status index (`venues_idx_open` на is_open, deleted_at)
- Soft delete partial indexes (WHERE deleted_at IS NULL)

**Query Optimization:**
- N+1 prevention (eager loading)
- Pagination на всех list endpoints
- Connection pooling (10-20 connections)
- Geo queries через Haversine formula или PostGIS

### 14.4. Geo Search Implementation

**Файл:** `src/utils/geo.py`

**Требования:**
- Реализация формулы Haversine для расчета расстояния
- Поддержка радиуса поиска в км
- Оптимизация через bounding box перед точным расчетом
- Индексация через `venues_idx_location`

---

## 15. Документация

### 15.1. API Documentation

**Auto-generated:**
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

**Requirements:**
- Все endpoints documented
- Request/response examples
- Error response schemas
- Authentication requirements
- Sync с venue-api.yaml через CI validation

### 15.2. Development Documentation

**Files:**
- `README.md` — Quick start, architecture overview
- `CONTRIBUTING.md` — Development guidelines
- `ARCHITECTURE.md` — Detailed architecture decisions
- `CHANGELOG.md` — Version history

### 15.3. Operations Documentation

**Files:**
- `RUNBOOK.md` — Incident response procedures
- `DEPLOYMENT.md` — Deployment procedures
- `MONITORING.md` — Alerting rules, dashboards

---

## 16. Чеклист Реализации

### Phase 1: Foundation (Week 1-2)
- [ ] Project structure setup
- [ ] uv + pyproject.toml configuration
- [ ] Database models (SQLAlchemy)
- [ ] Alembic migrations (на основе venue.sql)
- [ ] Basic FastAPI application
- [ ] Health check endpoints
- [ ] OpenAPI spec validation (venue-api.yaml)

### Phase 2: Core Features (Week 3-5)
- [ ] Companies CRUD endpoints
- [ ] Venues CRUD endpoints
- [ ] Payouts endpoints
- [ ] Geo search implementation
- [ ] Name search implementation
- [ ] Role-based authorization

### Phase 3: Integration (Week 6-7)
- [ ] RabbitMQ event publisher
- [ ] Gateway identity headers middleware
- [ ] gRPC client for Auth service
- [ ] Structured logging
- [ ] OpenTelemetry tracing
- [ ] Prometheus metrics

### Phase 4: Quality (Week 8-9)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Security scan
- [ ] Performance testing
- [ ] API contract validation

### Phase 5: Deployment (Week 10)
- [ ] Docker image
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Staging deployment
- [ ] Production deployment
- [ ] Monitoring dashboards

---

## 17. Риски и Митигация

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Geo search performance | Средняя | Высокое | PostGIS, caching, bounding box optimization |
| RabbitMQ message loss | Низкая | Критичное | Publisher confirms, retry logic, dead letter queue |
| Gateway header spoofing | Низкая | Критичное | Network isolation, IP whitelist, mTLS |
| Database connection exhaustion | Средняя | Высокое | Connection pooling, circuit breaker, monitoring |
| Money precision errors | Средняя | Высокое | Decimal type everywhere, validation, tests |

---

## 18. Примечания и Ограничения

1. **venue_documents таблица** — Исключена из текущей реализации согласно решению архитектуры. Может быть добавлена в будущих итерациях.

2. **Payouts POST endpoint** — Доступен только для admin. Staff может только просматривать историю выплат своего заведения.

3. **commission_rate** — Поле редактируется только admin. Staff не может изменять комиссию своего заведения.

4. **Soft Delete** — Все запросы к БД должны по умолчанию фильтровать `deleted_at IS NULL`. Admin может использовать `include_deleted=true`.

5. **Деньги** — Все денежные поля используют DECIMAL в БД и Decimal в Python. Не использовать float для финансовых расчетов.

6. **API Gateway** — Сервис доверяет заголовкам X-User-* только от доверенной сети Gateway. Прямые запросы без Gateway должны блокироваться.
