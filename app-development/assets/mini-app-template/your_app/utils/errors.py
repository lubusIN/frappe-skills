ERROR_CODES = {
    "VALIDATION_ERROR": "validation_error",
    "PERMISSION_DENIED": "permission_denied",
    "NOT_FOUND": "not_found",
    "INTEGRATION_ERROR": "integration_error",
    "APP_ERROR": "app_error",
}


HTTP_STATUS = {
    ERROR_CODES["VALIDATION_ERROR"]: 400,
    ERROR_CODES["PERMISSION_DENIED"]: 403,
    ERROR_CODES["NOT_FOUND"]: 404,
    ERROR_CODES["INTEGRATION_ERROR"]: 502,
    ERROR_CODES["APP_ERROR"]: 500,
}


def ok(message: str = "OK", data=None):
    return {
        "ok": True,
        "message": message,
        "data": data or {},
    }


def error(message: str, data=None, code: str | None = None):
    payload = {
        "ok": False,
        "message": message,
        "data": data or {},
    }
    if code:
        payload["code"] = code
        payload["http_status"] = HTTP_STATUS.get(code, 500)
    return payload
