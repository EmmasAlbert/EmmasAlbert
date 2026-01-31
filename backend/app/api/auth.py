from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

router = APIRouter()

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 密钥配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: str = "student"

class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str

class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    role: str
    avatar: Optional[str] = None
    is_active: bool
    created_at: datetime

def create_access_token(data: dict):
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    用户注册
    
    - **username**: 用户名（唯一）
    - **email**: 邮箱（唯一）
    - **password**: 密码（至少6位）
    - **phone**: 手机号（可选）
    - **role**: 角色（student/coach/admin，默认student）
    """
    # TODO: 实现数据库操作
    # 1. 检查用户名/邮箱是否已存在
    # 2. 密码加密
    # 3. 创建用户记录
    # 4. 返回用户信息
    
    return {
        "id": 1,
        "username": user_data.username,
        "email": user_data.email,
        "role": user_data.role,
        "avatar": None,
        "is_active": True,
        "created_at": datetime.now()
    }

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回JWT访问令牌
    """
    # TODO: 实现登录逻辑
    # 1. 验证用户名和密码
    # 2. 生成JWT token
    # 3. 返回token
    
    access_token = create_access_token(
        data={"sub": form_data.username, "role": "student"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/logout")
async def logout():
    """
    用户登出
    
    前端需要删除本地存储的token
    """
    return {"message": "Successfully logged out"}

@router.post("/reset-password")
async def reset_password(email: EmailStr):
    """
    重置密码
    
    发送重置密码邮件
    """
    # TODO: 实现密码重置逻辑
    # 1. 验证邮箱是否存在
    # 2. 生成重置令牌
    # 3. 发送邮件
    
    return {"message": "Password reset email sent"}

@router.post("/send-verification-code")
async def send_verification_code(phone: str):
    """
    发送验证码
    
    用于注册或找回密码
    """
    # TODO: 实现验证码发送
    # 1. 生成6位随机验证码
    # 2. 存储到Redis（5分钟有效）
    # 3. 调用短信服务发送
    
    return {"message": "Verification code sent", "expires_in": 300}
