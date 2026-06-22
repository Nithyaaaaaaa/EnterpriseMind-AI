from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token
)

from services.auth import (
    hash_password,
    verify_password,
    create_access_token
)

from dependencies.auth import get_current_user
from models.user import User
from fastapi import Depends

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400,detail="Email already registered")
    
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        form_data.password,
        existing_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
        "sub": existing_user.email,
        "user_id": existing_user.id,
        "role": existing_user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }

from dependencies.roles import require_role


@router.get("/admin")
def admin_only(
    current_user: User = Depends(
        require_role("admin")
    )
):
    return {
        "message": "Welcome Admin",
        "email": current_user.email,
        "role": current_user.role
    }