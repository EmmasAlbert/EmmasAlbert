from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class Post(BaseModel):
    """训练动态"""
    id: int
    user_id: int
    username: str
    avatar: Optional[str] = None
    content: str
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    likes: int
    comments: int
    created_at: datetime

class Comment(BaseModel):
    """评论"""
    id: int
    user_id: int
    username: str
    avatar: Optional[str] = None
    content: str
    created_at: datetime

@router.get("/feed", response_model=List[Post])
async def get_feed(skip: int = 0, limit: int = 20):
    """
    获取训练动态列表
    """
    return []

@router.post("/posts")
async def create_post(content: str, video_id: Optional[int] = None):
    """
    发布训练动态
    """
    return {
        "message": "Post created successfully",
        "post_id": 1
    }

@router.post("/posts/{post_id}/like")
async def like_post(post_id: int):
    """
    点赞动态
    """
    return {"message": "Post liked"}

@router.get("/posts/{post_id}/comments", response_model=List[Comment])
async def get_comments(post_id: int):
    """
    获取动态评论
    """
    return []

@router.post("/posts/{post_id}/comments")
async def create_comment(post_id: int, content: str):
    """
    评论动态
    """
    return {
        "message": "Comment created successfully",
        "comment_id": 1
    }

@router.get("/friends")
async def get_friends():
    """
    获取好友列表
    """
    return []

@router.post("/friends/{user_id}")
async def add_friend(user_id: int):
    """
    添加好友
    """
    return {"message": "Friend request sent"}

@router.delete("/friends/{user_id}")
async def remove_friend(user_id: int):
    """
    删除好友
    """
    return {"message": "Friend removed"}

@router.get("/notifications")
async def get_notifications():
    """
    获取通知列表
    """
    return []

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int):
    """
    标记通知为已读
    """
    return {"message": "Notification marked as read"}
