from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserLogin, UserOut
from app.models.user import User
from app.database import SessionLocal
from app.utils import hash_password, verify_password
from app.jwt import create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# REGISTER
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # user borligini tekshirish
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username yoki email allaqachon mavjud"
        )

    # password hash
    hashed_pwd = hash_password(user.password)

    # user yaratish
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# LOGIN
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Username not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Password not correct")

    token = create_access_token({"sub": db_user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ME (protected route)
@router.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    return {"user": current_user}