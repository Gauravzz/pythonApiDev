from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from sqlmodel import SQLModel, Field
from .routers import post, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
# function
async def root():
    return {"message": "Hello World"}




