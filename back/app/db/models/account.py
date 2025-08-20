from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, AuditMixin
from enum import Enum
from sqlalchemy import Enum as SAEnum

class UserRole(str, Enum):
    ADMIN = "admin"
    # позже можно добавить USER, MANAGER и т.д.

class Account(Base, AuditMixin):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)

    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)  # хранить хэш, не plain text

    # ссылка на организацию (если позже добавите organisations)
    organisation_id = Column(Integer, ForeignKey("organisations.id"), nullable=True)

    role = Column(SAEnum(UserRole, name="role_enum"), nullable=False, default=UserRole.ADMIN)
    organisation = relationship("Organisation", back_populates="accounts")

    __table_args__ = (
        UniqueConstraint("username", name="uq_accounts_username"),
        UniqueConstraint("email", name="uq_accounts_email"),
    )


class Organisation(Base, AuditMixin):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, index=True)

    organisation_name = Column(String(255), nullable=False)
    postal_address = Column(String(255), nullable=False)
    legal_form = Column(String(100), nullable=False)
    inn = Column(String(12), nullable=False)

    accounts = relationship("Account", back_populates="organisation")
