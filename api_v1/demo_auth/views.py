import secrets
import uuid
from time import time
from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(
    prefix="/demo-auth",
    tags=["Demo Auth"],
)

security = HTTPBasic()


@router.get("/basic-auth/")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> dict[str, str]:
    return {
        "You're authenticated": "True",
        "username": credentials.username,
        "password": credentials.password,
    }


usernames_to_passwords = {
    "admin": "admin",
    "John": "password",
}


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> dict[str, str] | str:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    if credentials.username not in usernames_to_passwords:
        raise unauthed_exc

    correct_password = usernames_to_passwords[credentials.username].encode("utf-8")
    if not correct_password:
        raise unauthed_exc
    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        correct_password,
    ):
        raise unauthed_exc
    return credentials.username


static_auth_token_to_username = {
    "dd6dbf40b28568f158b64f1bc67face7d3a": "admin",
    "eb7a9d45337cabf36f769b1de1337e0d5f3": "John",
}


def get_username_by_static_auth_roken(
    static_auth_token: str = Header(alias="x-auth-token"),
) -> dict[str, str] | str:
    if username := static_auth_token_to_username.get(static_auth_token):
        return username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid static auth token",
    )


@router.get("/basic-auth-username/")
def demo_basic_auth_username(
    auth_username: str = Depends(get_auth_user_username),
) -> dict[str, str]:
    return {
        "message": f"You're authenticated, {auth_username}",
        "username": auth_username,
    }


@router.get("/some-http-header-auth/")
def demo_auth_some_http_header(
    username: str = Depends(get_username_by_static_auth_roken),
) -> dict[str, str]:
    return {
        "message": f"You're authenticated, {username}",
        "username": username,
    }


cookies: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex


@router.post("/login-cookie/")
def demo_auth_login_set_cookie(
    response: Response,
    # auth_username: str = Depends(get_auth_user_username),
    username: str = Depends(get_username_by_static_auth_roken),
) -> dict[str, str]:
    session_id = generate_session_id()
    cookies[session_id] = {
        "username": username,
        "login_at": int(time()),
    }
    response.set_cookie(COOKIE_SESSION_ID_KEY, session_id)
    return {"result": "ok"}


def get_session_data(
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
) -> dict:
    if session_id not in cookies:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return cookies[session_id]


@router.get("/check-cookie/")
def demo_auth_check_cookie(
    user_session_data: dict = Depends(get_session_data),
) -> dict[str, str | int]:
    username = user_session_data.get("username")
    return {
        "message": f"Hi, {username}!",
        **user_session_data,
    }


@router.get("/logout-cookie/")
def demo_auth_logout_cookie(
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_ID_KEY),
    user_session_data: dict = Depends(get_session_data),
) -> dict[str, str]:
    cookies.pop(session_id, None)
    response.delete_cookie(COOKIE_SESSION_ID_KEY)
    username = user_session_data.get("username")
    return {
        "message": f"Bye, {username}!",
    }
