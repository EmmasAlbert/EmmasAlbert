from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class Achievement(BaseModel):
    """成就"""
    id: int
    name: str
    description: str
    icon: str
    achieved: bool
    achieved_at: Optional[datetime] = None

class LeaderboardEntry(BaseModel):
    """排行榜条目"""
    rank: int
    user_id: int
    username: str
    avatar: Optional[str] = None
    score: float
    value: int

@router.get("/", response_model=List[Achievement])
async def get_achievements():
    """
    获取成就列表
    """
    return [
        {
            "id": 1,
            "name": "初出茅庐",
            "description": "完成第一次训练",
            "icon": "🏀",
            "achieved": True,
            "achieved_at": datetime.now()
        },
        {
            "id": 2,
            "name": "百发百中",
            "description": "连续命中10球",
            "icon": "🎯",
            "achieved": False,
            "achieved_at": None
        }
    ]

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    type: str = "shooting_percentage",
    scope: str = "global",
    class_id: Optional[int] = None
):
    """
    获取排行榜
    
    - **type**: 排行类型（shooting_percentage/total_shots/training_time）
    - **scope**: 范围（global/class）
    - **class_id**: 班级ID（scope为class时必填）
    """
    return []

@router.get("/challenges")
async def get_challenges():
    """
    获取挑战任务列表
    """
    return {
        "daily_challenges": [
            {
                "id": 1,
                "title": "每日训练",
                "description": "完成一次训练",
                "reward": 10,
                "progress": 0,
                "target": 1,
                "completed": False
            }
        ],
        "weekly_challenges": [
            {
                "id": 2,
                "title": "本周训练达人",
                "description": "本周训练3次以上",
                "reward": 50,
                "progress": 1,
                "target": 3,
                "completed": False
            }
        ]
    }

@router.get("/user-stats")
async def get_user_stats():
    """
    获取用户统计数据
    """
    return {
        "total_points": 120,
        "total_achievements": 5,
        "rank": 15,
        "level": 3,
        "next_level_points": 50
    }
