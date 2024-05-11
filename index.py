# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["blog_db"]
posts_collection = db["posts"]

# Models
class Post(BaseModel):
    title: str
    content: str

class Comment(BaseModel):
    text: str

class Like(BaseModel):
    value: int

# Routes
@app.post("/posts/")
def create_post(post: Post):
    post_id = posts_collection.insert_one(post.dict()).inserted_id
    return {"id": str(post_id), "title": post.title, "content": post.content}

@app.get("/posts/", response_model=List[Post])
def read_posts():
    posts = list(posts_collection.find())
    return posts

@app.get("/posts/{post_id}", response_model=Post)
def read_post(post_id: str):
    post = posts_collection.find_one({"_id": post_id})
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}")
def update_post(post_id: str, post: Post):
    updated_post = posts_collection.update_one({"_id": post_id}, {"$set": post.dict()})
    if updated_post.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post updated successfully"}

@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    deleted_post = posts_collection.delete_one({"_id": post_id})
    if deleted_post.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}

@app.post("/posts/{post_id}/comments/")
def create_comment(post_id: str, comment: Comment):
    posts_collection.update_one({"_id": post_id}, {"$push": {"comments": comment.dict()}})
    return {"message": "Comment added successfully"}

@app.post("/posts/{post_id}/likes/")
def add_like(post_id: str, like: Like):
    posts_collection.update_one({"_id": post_id}, {"$inc": {"likes": like.value}})
    return {"message": "Like added successfully"}

@app.post("/posts/{post_id}/dislikes/")
def add_dislike(post_id: str, dislike: Like):
    posts_collection.update_one({"_id": post_id}, {"$inc": {"dislikes": dislike.value}})
    return {"message": "Dislike added successfully"}