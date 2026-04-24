from fastapi import HTTPException, status
from app.schemas.common import ErrorCode, ERROR_MESSAGES


class AppException(HTTPException):
    def __init__(
        self,
        error_code: int,
        message: str | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.error_code = error_code
        self.message = message or ERROR_MESSAGES.get(error_code, "未知错误")
        super().__init__(status_code=status_code, detail=self.message)


class UnauthorizedException(AppException):
    def __init__(
        self,
        error_code: int = ErrorCode.AUTH_NOT_LOGGED_IN,
        message: str | None = None,
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        error_code: int = ErrorCode.AUTH_PERMISSION_DENIED,
        message: str | None = None,
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundException(AppException):
    def __init__(
        self,
        error_code: int = ErrorCode.DOC_NOT_FOUND,
        message: str | None = None,
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class BadRequestException(AppException):
    def __init__(
        self,
        error_code: int = ErrorCode.PARAM_FORMAT_ERROR,
        message: str | None = None,
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InternalServerErrorException(AppException):
    def __init__(
        self,
        error_code: int = ErrorCode.SYS_INTERNAL_ERROR,
        message: str | None = None,
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
