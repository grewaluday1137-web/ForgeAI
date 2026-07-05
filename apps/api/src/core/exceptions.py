from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from jose import JWTError

class AppException(Exception):
    """Base application exception with HTTP status code and detail."""
    def __init__(self, status_code: int, detail: str, code: str = "error"):
        self.status_code = status_code
        self.detail = detail
        self.code = code
        super().__init__(detail)

class AuthException(AppException):
    def __init__(self, detail: str = "Authentication failed", code: str = "auth_error"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, code=code)

class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code="forbidden")

class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found", code="not_found")

class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, code="conflict")

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Transforms Pydantic's deeply nested validation errors into clean, readable messages."""
    errors = []
    for error in exc.errors():
        loc = " → ".join(str(l) for l in error["loc"] if l != "body")
        msg = error["msg"].replace("Value error, ", "")
        errors.append({"field": loc, "message": msg})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors[0]["message"] if len(errors) == 1 else "Validation failed",
            "code": "validation_error",
            "errors": errors,
        },
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all to prevent raw Python tracebacks reaching the client."""
    print(f"[UNHANDLED EXCEPTION] {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again.", "code": "internal_error"},
    )
