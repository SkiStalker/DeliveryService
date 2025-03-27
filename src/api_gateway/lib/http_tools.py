from fastapi import HTTPException


def make_http_error(resp):
    raise HTTPException(
        status_code=resp.code,
        detail=resp.message,
        headers={"WWW-Authenticate": "Bearer"},
    )
