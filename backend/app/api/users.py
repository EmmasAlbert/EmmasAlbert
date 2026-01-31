from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

class UserProfile(BaseModel):
    """用户资料"""
    real_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[datetime] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    arm_span: Optional[float] = None
    hand_size: Optional[float] = None
    basketball_experience: Optional[int] = None
    position_preference: Optional[str] = None

class UserInfo(BaseModel):
    """用户完整信息"""
    id: int
    username: str
    email: str
    role: str
    avatar: Optional[str] = None
    profile: Optional[UserProfile] = None

@router.get("/profile", response_model=UserInfo)
async def get_profile():
    """
    获取当前用户信息
    
    需要认证
    """
    # TODO: 从token获取用户ID，查询数据库
    return {
        "id": 1,
        "username": "student01",
        "email": "student@example.com",
        "role": "student",
        "avatar": None,
        "profile": None
    }

@router.put("/profile")
async def update_profile(profile: UserProfile):
    """
    更新用户资料
    
    可更新的字段：
    - real_name: 真实姓名
    - gender: 性别
    - birth_date: 出生日期
    - height: 身高(cm)
    - weight: 体重(kg)
    - arm_span: 臂展(cm)
    - hand_size: 手掌大小(cm)
    - basketball_experience: 篮球经验(年)
    - position_preference: 位置偏好
    """
    # TODO: 更新数据库
    return {"message": "Profile updated successfully", "data": profile}

@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    """
    上传用户头像
    
    支持格式：jpg, jpeg, png, gif
    最大大小：5MB
    """
    # TODO: 
    # 1. 验证文件类型和大小
    # 2. 上传到MinIO
    # 3. 更新用户表的avatar字段
    
    return {
        "message": "Avatar uploaded successfully",
        "avatar_url": f"/media/avatars/{file.filename}"
    }

@router.get("/{user_id}", response_model=UserInfo)
async def get_user(user_id: int):
    """
    获取指定用户信息
    
    用于查看其他用户资料
    """
    # TODO: 查询数据库
    return {
        "id": user_id,
        "username": f"user{user_id}",
        "email": f"user{user_id}@example.com",
        "role": "student",
        "avatar": None,
        "profile": None
    }

@router.get("/", response_model=List[UserInfo])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    search: Optional[str] = None
):
    """
    获取用户列表
    
    - **skip**: 跳过记录数（分页）
    - **limit**: 返回记录数（分页）
    - **role**: 角色筛选
    - **search**: 搜索关键词（用户名/邮箱）
    """
    # TODO: 查询数据库
    return []
