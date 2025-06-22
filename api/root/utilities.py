from rest_framework.response import Response

ACCESS_TOKEN_MAX_AGE = 300  # 5 minutes
REFRESH_TOKEN_MAX_AGE = 604800  # 7 days

def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=ACCESS_TOKEN_MAX_AGE,
    )

def set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Strict",
        max_age=REFRESH_TOKEN_MAX_AGE,
    )

def delete_token_cookies(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
