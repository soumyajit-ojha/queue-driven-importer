from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token
from app.security import get_hashed_password, verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # check existing user
    print("USER DATA", data)
    result = await db.execute(select(User).where(User.email == data.email))
    print("RESULT", result)
    existing = result.scalar_one_or_none()
    print("Hashed password 🔨🔨🔨", get_hashed_password(data.password))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        new_user = User(
            username=data.username,
            email=data.email,
            hashed_password=get_hashed_password(data.password)
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        token = create_access_token({"sub": new_user.email})
        return Token(access_token=token, token_type="bearer")
    except Exception as e:
        print("Error", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="newuser error."
        )

@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return Token(access_token=token, token_type="bearer")
