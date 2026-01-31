from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

class Course(BaseModel):
    """课程信息"""
    id: int
    title: str
    description: str
    level: str
    duration: int
    video_count: int
    thumbnail: Optional[str] = None

class Video(BaseModel):
    """教学视频"""
    id: int
    title: str
    description: str
    url: str
    duration: int
    thumbnail: Optional[str] = None

@router.get("/", response_model=List[Course])
async def list_courses(
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    """
    获取课程列表
    
    - **level**: 课程级别（beginner/intermediate/advanced）
    """
    return [
        {
            "id": 1,
            "title": "投篮基础入门",
            "description": "学习正确的投篮姿势和基本动作",
            "level": "beginner",
            "duration": 1800,
            "video_count": 10,
            "thumbnail": None
        }
    ]

@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: int):
    """
    获取课程详情
    """
    return {
        "id": course_id,
        "title": "投篮基础入门",
        "description": "学习正确的投篮姿势和基本动作",
        "level": "beginner",
        "duration": 1800,
        "video_count": 10,
        "thumbnail": None
    }

@router.get("/{course_id}/videos", response_model=List[Video])
async def get_course_videos(course_id: int):
    """
    获取课程视频列表
    """
    return []

@router.post("/{course_id}/enroll")
async def enroll_course(course_id: int):
    """
    报名课程
    """
    return {"message": "Successfully enrolled in course"}

@router.get("/progress/{course_id}")
async def get_course_progress(course_id: int):
    """
    获取课程学习进度
    """
    return {
        "course_id": course_id,
        "total_videos": 10,
        "completed_videos": 3,
        "progress_percentage": 30.0,
        "last_watched_at": datetime.now()
    }
