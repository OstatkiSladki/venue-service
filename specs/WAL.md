# WAL.md — Write-Ahead Log (состояние сессии)

## Current Phase
**VENUE-SPRINT-2: Stabilization + Public Schema + Venues Read/Write — IN PROGRESS**

## Completed
- `spec://project.venue-service/venue-spec#project-structure` — стабилизирован единый app entrypoint (`src.app`) и поправлены import-цепочки API v1.
- `spec://project.venue-service/venue-spec#configuration` — сохранен typed config; добавлен trusted-networks parsing для gateway auth.
- `spec://project.venue-service/venue-spec#database` — ORM модели переведены на default schema `public` (без явного `schema=...`).
- `spec://project.venue-service/venue-spec#migrations` — baseline миграция обновлена на `public`; добавлена миграция `20260324_0002` для безопасного переноса `venue -> public`.
- `spec://project.venue-service/venue-spec#security.headers` — добавлен `GatewayAuthMiddleware` с валидацией заголовков и trusted network проверкой.
- `spec://project.venue-service/venue-spec#venues-api` — добавлен слой `VenueRepository`/`VenueService` и роутер `/api/v1/venues` (list/get/create/update/delete soft).
- `spec://project.venue-service/venue-spec#authorization` — реализован RBAC для venues: admin full, staff create/update в рамках своей компании, user read-only.
- `spec://project.venue-service/venue-spec#error-handling` — error envelope подтвержден и синхронизирован для middleware/exception handler.
- `spec://project.venue-service/venue-spec#contract` — `venue-api.yaml` обновлен: list responses через paginated envelope, исправлен `PATCH /companies` indentation, Error schema приведена к runtime формату.
- `spec://project.venue-service/venue-spec#sql-baseline` — `specs/common/venue.sql` обновлен на `public` schema.

## In Progress
### DONE
- `spec://project.venue-service/venue-spec#tests` — расширен тестовый набор: bootstrap smoke, auth middleware checks, OpenAPI contract smoke, venue service RBAC tests.

### TODO
- `spec://project.venue-service/venue-spec#ci` — добавить CI pipeline с обязательными `pytest`, `mypy`, `ruff` и migration checks.
- `spec://project.venue-service/venue-spec#events` — подготовить event seam для future RabbitMQ integration (без runtime publish).
- `spec://project.venue-service/venue-spec#venues-geo` — усилить geo-search (bounding box + perf checks) и покрыть интеграционными тестами.

## Known Issues
1. Для staff company-scope в create/update venues используется вывод company через `X-User-Venue-ID` -> lookup venue. Это работает в текущем контракте, но требует отдельной валидации на целостность staff profile в Auth сервисе на следующем этапе.
2. Контракт payouts list уже стандартизирован как paginated envelope в `venue-api.yaml`, но runtime payouts endpoint еще не реализован (это ожидаемо, не regression).

## Decisions Pending
- Нужен ли отдельный header/claim для `staff_company_id`, чтобы убрать косвенное определение company через `X-User-Venue-ID`.

## Session Context
- **Start with**: прогнать `uv run pytest`, `uv run mypy src`, `uv run ruff check .`.
- **Key files**:
  - `src/app.py`
  - `src/middleware/auth.py`
  - `src/api/v1/venues.py`
  - `src/services/venue_service.py`
  - `alembic/versions/20260324_0002_migrate_venue_schema_to_public.py`
- **Watch out**: не нарушить текущий `public` schema контракт и не ослабить trusted network проверки middleware.
