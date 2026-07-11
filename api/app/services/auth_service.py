from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import (
    UserLoginRequest,
    UserRegisterRequest,
    UserRegisterResponse,
)


class AuthService:

    @staticmethod
    def register_user(
        db: Session,
        request: UserRegisterRequest,
    ) -> UserRegisterResponse:

        if user_repository.exists_by_email(
            db,
            request.email,
        ):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists.",
            )

        if user_repository.exists_by_username(
            db,
            request.username,
        ):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            )

        new_user = User(
            username=request.username,
            email=request.email,
            hashed_password=hash_password(
                request.password
            ),
        )

        try:

            created_user = user_repository.create(
                db,
                new_user,
            )

        except Exception:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists.",
            )

        return UserRegisterResponse(
            id=created_user.id,
            email=created_user.email,
            tenant_id=created_user.tenant_id,
        )

    @staticmethod
    def login(
        db: Session,
        request: UserLoginRequest,
    ):

        user = user_repository.get_by_email(
            db,
            request.email,
        )

        if user is None:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )

        if not verify_password(
            request.password,
            user.hashed_password,
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
            )

        token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "tenant_id": user.tenant_id,
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }


auth_service = AuthService()
