class AppError(Exception):
    status_code: int = 500
    detail: str = "内部服务器错误"
    code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str | None = None, code: str | None = None):
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"

    def __init__(self, detail: str = "资源不存在"):
        super().__init__(detail=detail)


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"

    def __init__(self, detail: str = "资源冲突"):
        super().__init__(detail=detail)


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"

    def __init__(self, detail: str = "未授权"):
        super().__init__(detail=detail)


class RateLimitError(AppError):
    status_code = 429
    code = "RATE_LIMIT"

    def __init__(self, detail: str = "请求过于频繁"):
        super().__init__(detail=detail)


class ValidationError(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"

    def __init__(self, detail: str = "请求参数无效"):
        super().__init__(detail=detail)


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"

    def __init__(self, detail: str = "无权访问"):
        super().__init__(detail=detail)


class BadRequestError(AppError):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, detail: str = "错误的请求"):
        super().__init__(detail=detail)


class InternalServerError(AppError):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, detail: str = "内部服务器错误"):
        super().__init__(detail=detail)
