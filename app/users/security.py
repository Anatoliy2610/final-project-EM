from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext


from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY_TOKEN


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_password_hash(password: str):
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY_TOKEN, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY_TOKEN, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
