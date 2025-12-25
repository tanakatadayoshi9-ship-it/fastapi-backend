from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    require_admin,
)

router = APIRouter(tags=["Users"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    auth_user = authenticate_user(db, user.username, user.password)
    if not auth_user:
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": auth_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.put("/users/{user_id}", dependencies=[Depends(require_admin)])
def update_user_role(
    user_id: int,
    data: schemas.RoleUpdate,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(404)
    user.role = data.role
    db.commit()
    return {"message": "User updated"}


@router.delete("/users/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(404)
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
