# WAL.md — Write-Ahead Log (состояние сессии)

## Current Phase
**VENUE-SPRINT-2: Stabilization + Public Schema + Venues Read/Write — IN PROGRESS**

## Completed
- `spec://project.venue-service/venue-spec#project-structure` — стабилизирован единый app entrypoint (`src.app`) и поправлены import-цепочки API v1.
- `spec://project.venue-service/venue-spec#configuration` — сохранен typed config; network-level IP checks исключены в текущей фазе.
- `spec://project.venue-service/venue-spec#database` — ORM модели переведены на default schema `public` (без явного `schema=...`).
- `spec://project.venue-service/venue-spec#migrations` — baseline миграция обновлена на `public`; добавлена миграция `20260324_0002` для безопасного переноса `venue -> public`.
- `spec://project.venue-service/venue-spec#security.headers` — `GatewayAuthMiddleware` валидирует только gateway identity headers (`X-User-*`) без IP whitelist.
- `spec://project.venue-service/venue-spec#venues-api` — добавлен слой `VenueRepository`/`VenueService` и роутер `/api/v1/venues` (list/get/create/update/delete soft).
- `spec://project.venue-service/venue-spec#authorization` — реализован RBAC для venues: admin full, staff create/update в рамках своей компании, user read-only.
- `spec://project.venue-service/venue-spec#error-handling` — error envelope подтвержден и синхронизирован для middleware/exception handler.
- `spec://project.venue-service/venue-spec#contract` — `venue-api.yaml` обновлен: list responses через paginated envelope, исправлен `PATCH /companies` indentation, Error schema приведена к runtime формату.
- `spec://project.venue-service/venue-spec#sql-baseline` — `specs/common/venue.sql` обновлен на `public` schema.
- `spec://project.venue-service/venue-spec#payouts-api` — реализован runtime payouts slice: `PayoutRepository`/`PayoutService`/`/api/v1/venues/{venue_id}/payouts` (GET list + POST create) с RBAC по ролям.
- `spec://project.venue-service/venue-spec#events` — добавлен event seam: `src/events/{topics,schemas,publisher}.py`, `NoopEventPublisher`, публикация `payout.created` после успешного create payout (без реального AMQP runtime).
- `spec://project.venue-service/venue-spec#tests` — добавлены unit/integration тесты для payouts + расширен OpenAPI/bootstrapping smoke.
- `spec://project.venue-service/venue-spec#quality-gates` — baseline стабилизирован: `uv run pytest`, `uv run mypy src`, `uv run ruff check .` проходят успешно.
- `spec://project.venue-service/venue-spec#api-layer` — list query параметры в `api/v1` унифицированы через Pydantic query schemas и передаются в service layer как typed filter objects.
- `spec://project.venue-service/venue-spec#contract` — `GET /venues/{venue_id}/payouts` дополнен query параметрами `limit/offset` в `venue-api.yaml`.

## In Progress
### DONE
- `spec://project.venue-service/venue-spec#tests` — расширен тестовый набор: bootstrap smoke, auth middleware checks, OpenAPI contract smoke, venue service RBAC tests.

### TODO
- `spec://project.venue-service/venue-spec#ci` — добавить CI pipeline с обязательными `pytest`, `mypy`, `ruff` и migration checks.
- `spec://project.venue-service/venue-spec#events` — заменить `NoopEventPublisher` на реальный RabbitMQ publisher (`aio-pika`, confirm/retry, DLQ policy, telemetry).
- `spec://project.venue-service/venue-spec#venues-geo` — усилить geo-search (bounding box + perf checks) и покрыть интеграционными тестами.
- `spec://project.venue-service/venue-spec#payouts-api` — добавить публичный статусный flow (`paid/cancelled`) и синхронизировать изменение `venue.payout_balance` на переходе в `paid`.

## Known Issues
1. Для staff company-scope в create/update venues используется вывод company через `X-User-Venue-ID` -> lookup venue. Это работает в текущем контракте, но требует отдельной валидации на целостность staff profile в Auth сервисе на следующем этапе.

## Decisions Pending
- Нужен ли отдельный header/claim для `staff_company_id`, чтобы убрать косвенное определение company через `X-User-Venue-ID`.
- Нужно ли возвращать network-level trust checks на этапе production hardening (вне текущей фазы разработки).

## Session Context
- **Start with**: прогнать `uv run pytest`, `uv run mypy src`, `uv run ruff check .`.
- **Key files**:
  - `src/app.py`
  - `src/middleware/auth.py`
  - `src/api/v1/venues.py`
  - `src/api/v1/payouts.py`
  - `src/services/payout_service.py`
  - `src/events/publisher.py`
- **Watch out**: не нарушить текущий `public` schema контракт; при внедрении real RabbitMQ сохранить publish-after-commit и не менять `payout_balance` на create.
