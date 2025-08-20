import logging

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.db.session import get_db
from app.db.models.account import Account
from app.core.config import settings
from app.db.schemas.result import OperationResult

from sqlalchemy.future import select

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
manager = LoginManager(SECRET_KEY, token_url="/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Загружаем пользователя по username
@manager.user_loader()
async def load_user(username: str, db: AsyncSession = None):
    if db is None:
        return None
    result = await db.execute(
        select(Account).where(Account.username == username)
    )
    return result.scalar_one_or_none()

# Эндпоинт логина
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    print("=>")
    logging.debug(form_data)
    user = await load_user(form_data.username, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = manager.create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return OperationResult.ok(data={"access_token": access_token})
