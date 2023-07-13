from fastapi import HTTPException, status    

def bad_request(_detail):
    raise HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        detail = _detail
    )    

def unauthorized(_detail):
    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = _detail,
        headers = {"WWW-Authenticate": "Bearer"}
    )

def forbidden(_detail):
    raise HTTPException(
        status_code = status.HTTP_403_FORBIDDEN,
        detail = _detail
    )

def not_found(_detail):
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = _detail
    )

def server_error(_detail):
    raise HTTPException(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail = _detail
    )