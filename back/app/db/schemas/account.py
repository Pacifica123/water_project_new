from pydantic import BaseModel, EmailStr
from datetime import datetime


# --- org ---

class OrganisationBase(BaseModel):
    organisation_name: str
    postal_address: str
    legal_form: str
    inn: str


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationUpdate(BaseModel):
    organisation_name: str | None = None
    postal_address: str | None = None
    legal_form: str | None = None
    inn: str | None = None


class OrganisationRead(OrganisationBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        orm_mode = True


# -- accounts --

class AccountBase(BaseModel):
    last_name: str
    first_name: str
    middle_name: str | None = None
    username: str
    email: EmailStr
    role: str


class AccountCreate(AccountBase):
    password: str
    organisation_id: int | None = None


class AccountUpdate(BaseModel):
    last_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None
    organisation_id: int | None = None


class AccountRead(AccountBase):
    id: int
    organisation: OrganisationRead | None = None
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        orm_mode = True



