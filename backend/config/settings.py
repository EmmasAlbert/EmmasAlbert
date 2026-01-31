from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """系统配置"""
    
    # 应用配置
    APP_NAME: str = "Basketball Training Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/basketball_training"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_VIDEOS: str = "training-videos"
    MINIO_BUCKET_IMAGES: str = "training-images"
    
    # AI模型配置
    YOLO_MODEL_PATH: str = "./models/yolov8n.pt"
    POSE_MODEL: str = "mediapipe"
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".avi", ".mov", ".mkv"}
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif"}
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # CORS配置
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
