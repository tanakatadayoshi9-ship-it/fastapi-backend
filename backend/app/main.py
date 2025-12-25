from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import engine, get_db
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    require_admin,
)
from app.routes import projects

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio API")

app.include_router(projects.router)


@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(
        (models.User.username == user.username)
        | (models.User.email == user.email)
    ).first()
    if exists:
        raise HTTPException(400, "User already exists")

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@app.put("/users/{user_id}/role")
def update_role(
    user_id: int,
    data: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.role = data.role
    db.commit()
    return {"detail": "Role updated"}
































