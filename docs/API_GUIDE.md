# API使用指南

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: JWT Bearer Token
- **请求格式**: JSON
- **响应格式**: JSON

## 认证流程

### 1. 用户注册

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "student01",
  "email": "student01@example.com",
  "password": "password123",
  "phone": "13800138000",
  "role": "student"
}
```

响应：
```json
{
  "id": 1,
  "username": "student01",
  "email": "student01@example.com",
  "role": "student",
  "avatar": null,
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

### 2. 用户登录

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=student01&password=password123
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. 使用Token访问受保护接口

```http
GET /api/users/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 训练管理接口

### 上传训练视频

```http
POST /api/training/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (binary video file)
title: "投篮练习"
```

响应：
```json
{
  "video_id": 1,
  "upload_url": "/media/videos/video_1.mp4",
  "message": "Video uploaded successfully. Analysis in progress."
}
```

### 获取视频分析结果

```http
GET /api/training/videos/1/analysis
Authorization: Bearer {token}
```

响应：
```json
{
  "video_id": 1,
  "total_shots": 20,
  "made_shots": 12,
  "missed_shots": 8,
  "shooting_percentage": 60.0,
  "avg_pose_score": 75.5,
  "shot_details": [
    {
      "shot_id": 1,
      "timestamp": 5.2,
      "result": "made",
      "pose_score": 80.0,
      "release_angle": 45.5
    }
  ],
  "recommendations": [
    "手肘角度需要增加至90度以上",
    "投篮时膝盖弯曲不足，建议降低重心"
  ]
}
```

### 获取训练记录

```http
GET /api/training/records?skip=0&limit=20
Authorization: Bearer {token}
```

响应：
```json
[
  {
    "id": 1,
    "training_type": "video",
    "duration": 1800,
    "total_shots": 30,
    "made_shots": 20,
    "shooting_percentage": 66.7,
    "avg_pose_score": 80.0,
    "created_at": "2024-01-20T10:00:00Z"
  }
]
```

## AI分析接口

### 投篮检测

```http
POST /api/analysis/shot-detection
Authorization: Bearer {token}
Content-Type: application/json

{
  "video_id": 1,
  "frame_id": 100
}
```

响应：
```json
{
  "shot_detected": true,
  "ball_trajectory": [[100, 200], [150, 180], [200, 160]],
  "hoop_position": [320, 100],
  "shot_result": "made",
  "release_point": [320, 400],
  "release_angle": 45.5,
  "ball_speed": 8.5
}
```

### 姿态分析

```http
POST /api/analysis/pose-analysis
Authorization: Bearer {token}
Content-Type: application/json

{
  "video_id": 1,
  "frame_id": 100
}
```

响应：
```json
{
  "keypoints": [...],
  "angles": {
    "elbow": 90.5,
    "knee": 135.2,
    "release_angle": 45.0
  },
  "pose_score": 85.0,
  "issues": ["手肘角度偏小", "膝盖未充分弯曲"],
  "suggestions": ["加大手肘弯曲至90度以上", "降低重心，增加膝盖弯曲"]
}
```

## WebSocket实时训练

### 连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/training/realtime/user_1');

ws.onopen = () => {
  console.log('Connected to training session');
};

// 发送视频帧
ws.send(JSON.stringify({
  type: 'frame',
  frame: base64EncodedFrame,
  timestamp: Date.now()
}));

// 接收分析结果
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'analysis_result') {
    console.log('Shot detected:', data.data.shot_detected);
    console.log('Pose score:', data.data.pose_score);
  }
};
```

## 错误处理

### 错误响应格式

```json
{
  "detail": "Error message"
}
```

### 常见错误码

- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或Token过期
- `403 Forbidden`: 无权限访问
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

### 示例错误响应

```json
{
  "detail": "Invalid token"
}
```

## 分页

所有列表接口支持分页参数：

- `skip`: 跳过记录数（默认0）
- `limit`: 返回记录数（默认20，最大100）

示例：
```http
GET /api/training/records?skip=20&limit=10
```

## 筛选和排序

支持筛选的接口：

```http
GET /api/training/records?training_type=video&start_date=2024-01-01
GET /api/users?role=student&search=john
```

## 速率限制

- 未认证用户：10次/分钟
- 认证用户：60次/分钟
- 视频上传：5次/小时

超过限制将返回 `429 Too Many Requests`

## 完整示例

### Python示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000/api"

# 登录
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "student01", "password": "password123"}
)
token = response.json()["access_token"]

# 设置认证头
headers = {
    "Authorization": f"Bearer {token}"
}

# 上传视频
with open("training.mp4", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/training/upload",
        headers=headers,
        files=files
    )
video_id = response.json()["video_id"]

# 获取分析结果
import time
time.sleep(10)  # 等待分析完成

response = requests.get(
    f"{BASE_URL}/training/videos/{video_id}/analysis",
    headers=headers
)
analysis = response.json()
print(f"命中率: {analysis['shooting_percentage']}%")
```

### JavaScript示例

```javascript
const BASE_URL = 'http://localhost:8000/api';

// 登录
async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });
  
  const data = await response.json();
  return data.access_token;
}

// 上传视频
async function uploadVideo(token, file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${BASE_URL}/training/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });
  
  return await response.json();
}

// 使用
const token = await login('student01', 'password123');
const result = await uploadVideo(token, videoFile);
console.log('Video uploaded:', result.video_id);
```

## 最佳实践

1. **Token管理**
   - 存储Token到localStorage或sessionStorage
   - Token过期前刷新
   - 登出时删除Token

2. **错误处理**
   - 总是检查响应状态码
   - 处理网络错误
   - 显示友好的错误提示

3. **性能优化**
   - 使用分页加载数据
   - 缓存常用数据
   - 压缩上传的视频文件

4. **安全性**
   - 使用HTTPS传输
   - 不在URL中传递敏感信息
   - 验证用户输入
