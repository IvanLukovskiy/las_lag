from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from api_v1.demo_auth.crud import user_db
from api_v1.demo_auth.helpers import create_access_token, create_refresh_token
from api_v1.demo_auth.validation import (
    get_current_auth_user,
    get_current_auth_user_for_refresh,
    get_current_token_payload,
)
from auth import utils as auth_utils
from users.schemas import UserSchema

http_bearer_scheme = HTTPBearer(auto_error=False)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


router = APIRouter(
    prefix="/jwt-auth",
    tags=["JWT"],
    dependencies=[Depends(http_bearer_scheme)],
)


def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
) -> UserSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    if not (user := user_db.get(username)):
        raise unauthed_exc

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


def get_current_active_user(
    user: UserSchema = Depends(get_current_auth_user),
) -> UserSchema:
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user",
    )


@router.post("/login/", response_model=TokenInfo)
def auth_user_issue_jwt(
    user: UserSchema = Depends(validate_auth_user),
) -> TokenInfo:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh/",
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
def auth_refresh_jwt(
    user: UserSchema = Depends(get_current_auth_user_for_refresh),
    # user: UserSchema = Depends(get_auth_user_from_token_of_type(REFRESH_TOKEN_TYPE)),
    # user: UserSchema = Depends(UserGetterFromToken(REFRESH_TOKEN_TYPE)),
) -> TokenInfo:
    access_token = create_access_token(user)
    return TokenInfo(
        access_token=access_token,
    )


@router.get("/users/me/")
def auth_user_check_self_info(
    user: UserSchema = Depends(get_current_active_user),
    payload: dict = Depends(get_current_token_payload),
) -> dict:
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
    }
