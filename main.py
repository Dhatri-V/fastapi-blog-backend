from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
import models
from database import engine, SessionLocal
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Pydantic model
class Post(BaseModel):
    title: str
    content: str

#Pydantic model for user registration.
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# DB session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Blog API is running"}


# GET all posts
@app.get("/posts")
def get_posts(db = Depends(get_db)):

    return db.query(models.PostDB).all()


# GET one post
@app.get("/posts/{post_id}")
def get_post(post_id: int, db = Depends(get_db)):

    post = db.query(models.PostDB).filter(
        models.PostDB.id == post_id
    ).first()

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


# CREATE post
@app.post("/posts")
def create_post(post: Post, db = Depends(get_db)):

    new_post = models.PostDB(
        title=post.title,
        content=post.content
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# UPDATE post
@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post, db = Depends(get_db)):

    db_post = db.query(models.PostDB).filter(
        models.PostDB.id == post_id
    ).first()

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    db_post.title = post.title
    db_post.content = post.content

    db.commit()
    db.refresh(db_post)

    return db_post


# DELETE post
@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db = Depends(get_db)):

    db_post = db.query(models.PostDB).filter(
        models.PostDB.id == post_id
    ).first()

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(db_post)
    db.commit()

    return {"message": "Post deleted"}

@app.post("/users")
def create_user(user: UserCreate, db = Depends(get_db)):

    hashed_password = pwd_context.hash(user.password)

    new_user = models.UserDB(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@app.post("/login")
def login(user: UserLogin, db = Depends(get_db)):

    db_user = db.query(models.UserDB).filter(
        models.UserDB.email == user.email
    ).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"message": "Login successful"}