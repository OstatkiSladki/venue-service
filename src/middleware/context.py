import structlog


def bind_request_context(request_id: str, user_id: str | None = None) -> None:
  values: dict[str, str] = {"request_id": request_id}
  if user_id is not None:
    values["user_id"] = user_id
  structlog.contextvars.bind_contextvars(**values)


def clear_request_context() -> None:
  structlog.contextvars.clear_contextvars()
