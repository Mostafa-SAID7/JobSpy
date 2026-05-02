from app.domain.entities.user import User
from app.infrastructure.persistence.sqlalchemy.models.user_orm import UserORM


class UserMapper:
    """Mapper to convert between User domain entity and UserORM model."""

    @staticmethod
    def to_domain(orm_user: UserORM) -> User:
        """Convert SQLAlchemy UserORM to User domain entity."""
        if not orm_user:
            return None
            
        return User(
            id=orm_user.id,
            email=orm_user.email,
            username=orm_user.username,
            full_name=orm_user.full_name,
            phone=orm_user.phone,
            bio=orm_user.bio,
            hashed_password=orm_user.hashed_password,
            is_active=orm_user.is_active,
            is_verified=orm_user.is_verified,
            created_at=orm_user.created_at,
            updated_at=orm_user.updated_at,
            last_login=orm_user.last_login
        )

    @staticmethod
    def to_orm(domain_user: User) -> UserORM:
        """Convert User domain entity to SQLAlchemy UserORM."""
        if not domain_user:
            return None
            
        return UserORM(
            id=domain_user.id,
            email=domain_user.email,
            username=domain_user.username,
            full_name=domain_user.full_name,
            phone=domain_user.phone,
            bio=domain_user.bio,
            hashed_password=domain_user.hashed_password,
            is_active=domain_user.is_active,
            is_verified=domain_user.is_verified,
            created_at=domain_user.created_at,
            updated_at=domain_user.updated_at,
            last_login=domain_user.last_login
        )
