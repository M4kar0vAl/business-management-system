from fastapi import status

from app.schemas import ErrorResponse, SuccessResponse

SUCCESS_RESPONSE = {
    status.HTTP_200_OK: {"model": SuccessResponse, "description": "Successful Response"}
}

BAD_REQUEST_RESPONSE = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorResponse,
        "description": "Bad Request Error",
    }
}

ALREADY_EXISTS_RESPONSE = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorResponse,
        "description": "Already Exists Error",
    }
}

UNAUTHORIZED_RESPONSE = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": ErrorResponse,
        "description": "Unauthorized Error",
    }
}

FORBIDDEN_RESPONSE = {
    status.HTTP_403_FORBIDDEN: {
        "model": ErrorResponse,
        "description": "Forbidden Error",
    }
}

NOT_FOUND_RESPONSE = {
    status.HTTP_404_NOT_FOUND: {
        "model": ErrorResponse,
        "description": "Not Found Error",
    }
}
