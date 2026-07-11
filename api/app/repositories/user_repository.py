from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:

        stmt = (
            select(User)
            .where(User.id == user_id)
        )

        return db.execute(
            stmt
        ).scalar_one_or_none()

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:

        stmt = (
            select(User)
            .where(User.email == email)
        )

        return db.execute(
            stmt
        ).scalar_one_or_none()

    @staticmethod
    def get_by_username(
        db: Session,
        username: str,
    ) -> User | None:

        stmt = (
            select(User)
            .where(User.username == username)
        )

        return db.execute(
            stmt
        ).scalar_one_or_none()

    @staticmethod
    def exists_by_email(
        db: Session,
        email: str,
    ) -> bool:

        return (
            UserRepository.get_by_email(
                db,
                email,
            )
            is not None
        )

    @staticmethod
    def exists_by_username(
        db: Session,
        username: str,
    ) -> bool:

        return (
            UserRepository.get_by_username(
                db,
                username,
            )
            is not None
        )

    @staticmethod
    def create(
        db: Session,
        user: User,
    ) -> User:

        try:

            db.add(user)

            db.commit()

            db.refresh(user)

            return user

        except IntegrityError:

            db.rollback()

            raise
            

user_repository = UserRepository()