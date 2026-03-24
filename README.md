# Venue Service

FastAPI сервис управления компаниями, заведениями и выплатами.

## Local run

```bash
uv run python main.py
```

## API

- `GET /health`
- `GET /ready`
- `GET /api/v1/companies`
- `POST /api/v1/companies`
- `GET /api/v1/companies/{company_id}`
- `PATCH /api/v1/companies/{company_id}`
- `DELETE /api/v1/companies/{company_id}`

## Migrations

```bash
uv run alembic upgrade head
```
