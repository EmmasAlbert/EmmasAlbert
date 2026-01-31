from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api import auth, users, training, analysis, courses, achievements, social
from app.middleware.auth_middleware import AuthMiddleware

# 创建FastAPI应用实例
app = FastAPI(
    title="Basketball Training Assistant System",
    description="基于YOLOv8的中小学生篮球训练辅助系统",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(training.router, prefix="/api/training", tags=["训练管理"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["AI分析"])
app.include_router(courses.router, prefix="/api/courses", tags=["课程管理"])
app.include_router(achievements.router, prefix="/api/achievements", tags=["成就系统"])
app.include_router(social.router, prefix="/api/social", tags=["社交互动"])

@app.get("/")
async def root():
    """系统首页"""
    return {
        "message": "Basketball Training Assistant System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/training/realtime/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """实时训练WebSocket连接"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # 接收视频帧数据
            data = await websocket.receive_json()
            
            # TODO: 调用AI引擎进行实时分析
            # analysis_result = await ai_engine.analyze_frame(data['frame'])
            
            # 发送分析结果
            await manager.send_message({
                "type": "analysis_result",
                "data": {
                    "shot_detected": False,
                    "pose_score": 0,
                    "timestamp": data.get('timestamp')
                }
            }, user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
