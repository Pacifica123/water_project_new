from fastapi import APIRouter, Depends

from app.db.session import get_db
from app.services.auth import login, manager
from app.db.schemas.result import OperationResult
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="", tags=["auth"])

@router.post("/login")
async def login_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    print("=>")
    return await login(form_data, db)


@router.get("/me")
async def get_me(user=Depends(manager)):
    # Здесь user — это объект Account
    return OperationResult.ok(
        data={"username": user.username, "role": user.role}
    )

@router.get("/test")
async def test():
    return {"msg": "auth test OK"}