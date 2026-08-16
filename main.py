from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import models
from database import engine,SessionLocal
from fastapi import Depends

class Post(BaseModel):
    title: str
    content: str


app = FastAPI()

models.Base.metadata.create_all(bind=engine)
posts = [
    {
        "id": 1,
        "title": "My First Post",
        "content": "Learning FastAPI"
    },
    {
        "id": 2,
        "title": "My Second Post",
        "content": "Building a blog backend"
    }
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Blog API is running"}

#display all the posts
@app.get("/posts")
def get_posts(db = Depends(get_db)):
    return db.query(models.PostDB).all()


@app.get("/posts/{post_id}")
def get_posts(post_id:int):
     for post in posts:

        if post["id"] == post_id:

            return post
     raise HTTPException(status_code=404, detail="Post not found")


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

@app.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):

    for p in posts:
        if p["id"] == post_id:
            p["title"] = post.title
            p["content"] = post.content
            return p

    raise HTTPException(status_code=404, detail="Post not found")


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):

    for post in posts:
        if post["id"] == post_id:
            posts.remove(post)
            return {"message": "Post deleted"}

    raise HTTPException(status_code=404, detail="Post not found")