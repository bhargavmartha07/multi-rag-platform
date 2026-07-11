from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserLoginRequest,
    UserMeResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> UserRegisterResponse:

    return auth_service.register_user(
        db,
        request,
    )


@router.post("/login")
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):

    return auth_service.login(
        db,
        request,
    )


@router.get(
    "/me",
    response_model=UserMeResponse,
)
def me(
    current_user: User = Depends(
        get_current_user
    ),
) -> UserMeResponse:

    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        tenant_id=current_user.tenant_id,
    )
