from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, auth

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.get("/")
async def read_root():
    return "Hello World Guys how are you i am fine and you"

@app.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = models.User(
        username=user.username,
        hashed_password=auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not db_user or not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = auth.create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
