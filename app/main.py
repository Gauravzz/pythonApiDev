from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from sqlmodel import SQLModel, Field

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


while True:

    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                                password='password', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("database connected correctly.")
        break
    except Exception as error:
        print("database connection fail")
        print("Error: ", error)
        time.sleep(2)

my_posts = [{"title": "Sugar the venom", "content": "void of discomfort & guilt.", "id": 1},
            {"title": "Milk the drug", "content": "suffering & empathy?", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i

# decorator(method, path)


@app.get("/")
# function
async def root():
    return {"message": "Hello World"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    return {"data": posts}
#working with orm here and this is """SELECT * FROM posts """ regualar.

# decorator(method, path)
@app.get("/posts")
# function
async def get_posts(db: Session = Depends(get_db)):
        # cursor.execute("""SELECT * FROM posts """)
        # posts = cursor.fetchall()
        posts = db.query(models.Post).all()
        return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
# extract all fields from body to python dictionary = payLoad (variable)
def create_posts(post: Post, db:Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                 (post.title,post.content,post.published))

    # new_post = cursor.fetchone()

    # conn.commit()
    new_post = models.Post(
        # title=post.title, content=post.content, published=post.published
        **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * from posts WHERE id = %s """, (str(id),))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    # print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found.")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id: {id} was not found."}
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # delete post
    # find the index in the array that has required ID
    # my_posts.pop(index)
                    # advance to advancer
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()    
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist :)")
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):
    
    # cursor.execute("""UPDATE posts SET title = %s, content= %s, published = %s WHERE id= %s RETURNING *""", (
    #     post.title, post.content, post.published, str(id)    
    # ))

    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist :)")

    # post_dict = post.dict()
    # post_dict['id'] = id
    # my_posts[index] = post_dict
    data = updated_post.__dict__.copy()
    data.pop("id", None)
    post_query.update(data, synchronize_session=False)

    db.commit()

    return {'data': post_query.first()}
