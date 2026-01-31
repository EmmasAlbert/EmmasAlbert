from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config.settings import settings

security = HTTPBearer()

class AuthMiddleware:
    """JWT认证中间件"""
    
    @staticmethod
    def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
        """
        验证JWT Token
        
        Args:
            credentials: HTTP认证凭证
            
        Returns:
            Token payload
            
        Raises:
            HTTPException: Token无效或过期
        """
        try:
            token = credentials.credentials
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )
