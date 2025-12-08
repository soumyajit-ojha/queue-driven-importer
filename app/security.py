"""
This module contains security settings
"""

from datetime import datetime, timezone, timedelta
import jwt
from decouple import config
from passlib.context import CryptContext
from fastapi import HTTPException, status
from typing import Optional
from app.schemas import TokenData


TOKEN_LIFE_MINUIT = int(config("ACCESS_TOKEN_LIFE_MINUIT"))
SECRET_KEY = config("SECRET_KEY")
ENCODE_ALGORITHM = config("ENCODE_ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the plain password and hashed password.
    by pwd_context
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_hashed_password(password: str) -> str:
    """
    Hashed password by pwd_context.
    """
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(400, "Password too long! Must be <= 72 characters")

    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Password hashing failed: {str(e)+str(password)}"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a acceess token for user.
    """

    encode_data = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_LIFE_MINUIT)

    encode_data.update({"exp": expire})
    encoded_jwt = jwt.encode(encode_data, SECRET_KEY, ENCODE_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ENCODE_ALGORITHM])

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unverified token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(email=email)

    except jwt.PyJWTError as e:
        # print(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credential.",
            headers={"WWW-Authenticate": "Bearer"},
        )
