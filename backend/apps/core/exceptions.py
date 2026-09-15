"""DRF exception handler -> structured error envelope."""

from rest_framework.views import exception_handler


def structured_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    response.data = {
        "error": {
            "status_code": response.status_code,
            "detail": response.data,
        }
    }
    return response
