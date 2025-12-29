# 📡 API文档

## 概述

本系统提供RESTful API接口，支持用户认证、视频处理、实时检测等功能。

**Base URL**: `http://localhost:5000`

**Content-Type**: `application/json`

## 认证接口

### 用户注册

注册新用户账号。

**端点**: `POST /api/register`

**请求体**:
```json
{
  "username": "string",      // 必填，用户名
  "password": "string",      // 必填，密码
  "email": "string",         // 可选，邮箱
  "full_name": "string"      // 可选，姓名
}
```

**响应**:
```json
{
  "success": true,
  "message": "注册成功",
  "user_id": 1
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "用户名已存在"
}
```

### 用户登录

用户登录并创建会话。

**端点**: `POST /api/login`

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "id": 1,
    "username": "test_user",
    "email": "test@example.com",
    "full_name": "测试用户",
    "created_at": "2025-01-01 00:00:00"
  }
}
```

### 用户登出

退出当前会话。

**端点**: `POST /api/logout`

**响应**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

### 获取用户信息

获取当前登录用户的信息。

**端点**: `GET /api/user/info`

**需要认证**: 是

**响应**:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "test_user",
    "email": "test@example.com",
    "full_name": "测试用户",
    "created_at": "2025-01-01 00:00:00",
    "last_login": "2025-01-02 10:30:00"
  }
}
```

## 视频处理接口

### 上传视频

上传训练视频文件。

**端点**: `POST /api/upload`

**需要认证**: 是

**Content-Type**: `multipart/form-data`

**请求参数**:
- `video`: 视频文件（支持mp4, avi, mov, mkv格式）

**响应**:
```json
{
  "success": true,
  "message": "上传成功",
  "filename": "1_20250101_120000_video.mp4",
  "filepath": "data/raw/1_20250101_120000_video.mp4"
}
```

### 处理视频

对上传的视频进行分析处理。

**端点**: `POST /api/process/video`

**需要认证**: 是

**请求体**:
```json
{
  "video_path": "data/raw/1_20250101_120000_video.mp4"
}
```

**响应**:
```json
{
  "success": true,
  "message": "处理完成",
  "session_id": 1,
  "results": {
    "total_shots": 15,
    "valid_shots": 12,
    "average_score": 75.5,
    "output_video": "outputs/videos/session_1_analyzed.mp4",
    "report": {
      "total_shots": 15,
      "valid_shots": 12,
      "average_score": 75.5,
      "score_distribution": {
        "excellent": 4,
        "good": 6,
        "needs_improvement": 2
      },
      "common_issues": [
        "✗ 肘部角度需调整",
        "✗ 建议提高出手点"
      ],
      "summary": "良好，投篮动作基本规范，注意改进细节。"
    }
  }
}
```

## 实时检测接口

### 处理摄像头帧

处理摄像头捕获的单帧图像。

**端点**: `POST /api/camera/frame`

**需要认证**: 是

**请求体**:
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."  // Base64编码的图像
}
```

**响应**:
```json
{
  "success": true,
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",  // 处理后的图像
  "detections": {
    "basketball": 1,
    "players": 1,
    "hoops": 1,
    "poses": 1
  },
  "analysis": {
    "elbow_angle": 85.5,
    "release_height": 1.35,
    "body_alignment": 8.2,
    "shooting_hand": "right",
    "form_score": 85.0,
    "feedback": [
      "✓ 肘部角度良好 (85.5°)",
      "✓ 出手高度适当",
      "✓ 身体对齐良好"
    ]
  }
}
```

## 训练历史接口

### 获取训练历史

获取用户的训练历史记录。

**端点**: `GET /api/training/history?limit=10`

**需要认证**: 是

**查询参数**:
- `limit`: 返回记录数量（默认10）

**响应**:
```json
{
  "success": true,
  "history": [
    {
      "id": 1,
      "user_id": 1,
      "session_date": "2025-01-01 14:30:00",
      "video_path": "data/raw/video.mp4",
      "duration": 180,
      "total_shots": 15,
      "successful_shots": 0,
      "average_score": 75.5,
      "notes": null
    }
  ]
}
```

### 获取训练记录详情

获取特定训练记录的详细分析数据。

**端点**: `GET /api/training/session/{session_id}`

**需要认证**: 是

**响应**:
```json
{
  "success": true,
  "analysis": [
    {
      "id": 1,
      "session_id": 1,
      "timestamp": 15.5,
      "elbow_angle": 85.5,
      "release_height": 1.35,
      "body_alignment": 8.2,
      "shooting_hand": "right",
      "form_score": 85.0,
      "feedback": "✓ 肘部角度良好 (85.5°)\n✓ 出手高度适当\n✓ 身体对齐良好"
    }
  ]
}
```

## 错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 错误响应格式

所有错误响应都遵循以下格式:

```json
{
  "success": false,
  "message": "错误描述信息"
}
```

## 使用示例

### Python示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:5000"

# 创建session以保持登录状态
session = requests.Session()

# 1. 注册
response = session.post(f"{BASE_URL}/api/register", json={
    "username": "test_user",
    "password": "test_password",
    "email": "test@example.com"
})
print(response.json())

# 2. 登录
response = session.post(f"{BASE_URL}/api/login", json={
    "username": "test_user",
    "password": "test_password"
})
print(response.json())

# 3. 上传视频
with open("basketball_video.mp4", "rb") as f:
    files = {"video": f}
    response = session.post(f"{BASE_URL}/api/upload", files=files)
    upload_result = response.json()
    print(upload_result)

# 4. 处理视频
response = session.post(f"{BASE_URL}/api/process/video", json={
    "video_path": upload_result["filepath"]
})
print(response.json())

# 5. 获取训练历史
response = session.get(f"{BASE_URL}/api/training/history?limit=5")
print(response.json())
```

### JavaScript示例

```javascript
const BASE_URL = "http://localhost:5000";

// 1. 登录
async function login() {
  const response = await fetch(`${BASE_URL}/api/login`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      username: 'test_user',
      password: 'test_password'
    })
  });
  const data = await response.json();
  console.log(data);
}

// 2. 上传视频
async function uploadVideo(file) {
  const formData = new FormData();
  formData.append('video', file);
  
  const response = await fetch(`${BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  console.log(data);
  return data.filepath;
}

// 3. 处理摄像头帧
async function processCameraFrame(imageData) {
  const response = await fetch(`${BASE_URL}/api/camera/frame`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({image: imageData})
  });
  const data = await response.json();
  return data;
}
```

### cURL示例

```bash
# 注册
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_password"}'

# 登录
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"test_password"}' \
  -c cookies.txt

# 上传视频
curl -X POST http://localhost:5000/api/upload \
  -b cookies.txt \
  -F "video=@basketball_video.mp4"

# 获取训练历史
curl -X GET http://localhost:5000/api/training/history?limit=10 \
  -b cookies.txt
```

## 速率限制

当前版本没有速率限制，但建议：
- 摄像头帧处理：每秒最多1次
- 视频上传：单个文件最大500MB
- 并发请求：建议不超过10个

## 认证说明

- 系统使用Session-based认证
- 登录后Session自动保存在Cookie中
- Session有效期：24小时
- 每次请求会自动验证Session

## 数据格式

### 投篮分析结果格式

```json
{
  "elbow_angle": 85.5,           // 肘部角度（度）
  "release_height": 1.35,        // 出手高度比例
  "body_alignment": 8.2,         // 身体对齐度（度）
  "shooting_hand": "right",      // 投篮手：left/right
  "form_score": 85.0,           // 姿势得分（0-100）
  "feedback": [                  // 反馈建议数组
    "✓ 肘部角度良好 (85.5°)",
    "✓ 出手高度适当",
    "✓ 身体对齐良好"
  ]
}
```

### 检测结果格式

```json
{
  "basketball": 1,    // 检测到的篮球数量
  "players": 1,       // 检测到的人数
  "hoops": 1,         // 检测到的篮筐数量
  "poses": 1          // 检测到的姿态数量
}
```

## 注意事项

1. 所有需要认证的接口必须先调用登录接口
2. 视频处理是异步操作，可能需要较长时间
3. 实时检测建议控制频率，避免服务器负载过高
4. Base64编码的图像数据较大，注意网络带宽

## 版本历史

- **v1.0.0** (2025-01-01): 初始版本发布

---

更多信息请参考 [README.md](README.md)
