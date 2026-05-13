"""Custom domain exceptions with HTTP status mapping."""


class AppError(Exception):
    """Base application error."""
    status_code: int = 500
    detail: str = "内部服务器错误"


class NotFoundError(AppError):
    status_code = 404

    def __init__(self, detail: str = "资源不存在"):
        self.detail = detail


class ConflictError(AppError):
    status_code = 409

    def __init__(self, detail: str = "资源冲突"):
        self.detail = detail


class UnauthorizedError(AppError):
    status_code = 401

    def __init__(self, detail: str = "未授权"):
        self.detail = detail


class RateLimitError(AppError):
    status_code = 429

    def __init__(self, detail: str = "请求过于频繁"):
        self.detail = detail


class ValidationError(AppError):
    status_code = 400

    def __init__(self, detail: str = "请求参数无效"):
        self.detail = detail
