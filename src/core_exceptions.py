from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AppError(Exception):
  code: str
  message: str
  status_code: int
  details: list[dict[str, Any]] | None = None


class ForbiddenError(AppError):
  def __init__(self, message: str = "Not enough permissions") -> None:
    super().__init__(code="FORBIDDEN", message=message, status_code=403)


class UnauthorizedError(AppError):
  def __init__(self, message: str = "Authentication required") -> None:
    super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class NotFoundError(AppError):
  def __init__(self, message: str = "Resource not found") -> None:
    super().__init__(code="NOT_FOUND", message=message, status_code=404)


class ConflictError(AppError):
  def __init__(self, message: str = "Conflict") -> None:
    super().__init__(code="CONFLICT", message=message, status_code=409)
