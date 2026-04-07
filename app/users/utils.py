from fastapi.responses import JSONResponse


async def get_response(access_token):
    response = JSONResponse(
        content={"access_token": access_token, "refresh_token": None}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Защита от XSS
        samesite="lax",  # Защита от CSRF
    )
    return response
