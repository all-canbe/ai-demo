from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorCode:
    SUCCESS = 0

    AUTH_NOT_LOGGED_IN = 1001
    AUTH_TOKEN_EXPIRED = 1002
    AUTH_PERMISSION_DENIED = 1003
    AUTH_USER_EXISTS = 1004
    AUTH_INVALID_CREDENTIALS = 1005
    AUTH_INVALID_TOKEN = 1006

    PARAM_MISSING = 2001
    PARAM_FORMAT_ERROR = 2002
    PARAM_FILE_TYPE_NOT_SUPPORTED = 2003
    PARAM_FILE_TOO_LARGE = 2004

    DOC_UPLOAD_FAILED = 3001
    DOC_PARSE_FAILED = 3002
    DOC_NOT_FOUND = 3003
    DOC_PROCESSING = 3004

    CHAT_SESSION_NOT_FOUND = 4001
    CHAT_MESSAGE_EMPTY = 4002
    CHAT_LLM_FAILED = 4003

    SYS_INTERNAL_ERROR = 5001
    SYS_DB_CONNECTION_FAILED = 5002
    SYS_EXTERNAL_SERVICE_UNAVAILABLE = 5003


ERROR_MESSAGES: dict[int, str] = {
    ErrorCode.SUCCESS: "success",
    ErrorCode.AUTH_NOT_LOGGED_IN: "未登录，请先登录",
    ErrorCode.AUTH_TOKEN_EXPIRED: "Token已过期，请重新登录",
    ErrorCode.AUTH_PERMISSION_DENIED: "权限不足",
    ErrorCode.AUTH_USER_EXISTS: "该邮箱已注册",
    ErrorCode.AUTH_INVALID_CREDENTIALS: "邮箱或密码错误",
    ErrorCode.AUTH_INVALID_TOKEN: "无效的Token",
    ErrorCode.PARAM_MISSING: "参数缺失",
    ErrorCode.PARAM_FORMAT_ERROR: "参数格式错误",
    ErrorCode.PARAM_FILE_TYPE_NOT_SUPPORTED: "不支持的文件类型",
    ErrorCode.PARAM_FILE_TOO_LARGE: "文件大小超过限制",
    ErrorCode.DOC_UPLOAD_FAILED: "文档上传失败",
    ErrorCode.DOC_PARSE_FAILED: "文档解析失败",
    ErrorCode.DOC_NOT_FOUND: "文档不存在",
    ErrorCode.DOC_PROCESSING: "文档正在处理中",
    ErrorCode.CHAT_SESSION_NOT_FOUND: "聊天会话不存在",
    ErrorCode.CHAT_MESSAGE_EMPTY: "问题不能为空",
    ErrorCode.CHAT_LLM_FAILED: "LLM调用失败，请稍后重试",
    ErrorCode.SYS_INTERNAL_ERROR: "内部服务错误",
    ErrorCode.SYS_DB_CONNECTION_FAILED: "数据库连接失败",
    ErrorCode.SYS_EXTERNAL_SERVICE_UNAVAILABLE: "外部服务不可用",
}
