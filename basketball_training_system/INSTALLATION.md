# 📦 安装指南

## 系统要求

### 最低配置
- **操作系统**: Windows 10/11, Ubuntu 18.04+, macOS 10.14+
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM
- **硬盘**: 2GB 可用空间
- **浏览器**: Chrome 90+, Firefox 88+, Edge 90+

### 推荐配置
- **操作系统**: Windows 11, Ubuntu 20.04+, macOS 11+
- **Python**: 3.9 或 3.10
- **内存**: 8GB RAM 或更高
- **GPU**: NVIDIA GPU（可选，用于加速）
- **硬盘**: 5GB 可用空间
- **摄像头**: 720p 或更高分辨率

## 详细安装步骤

### Windows系统

#### 1. 安装Python

1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载 Python 3.8+ 安装包
3. 运行安装程序
4. **重要**: 勾选 "Add Python to PATH"
5. 点击 "Install Now"

验证安装:
```cmd
python --version
pip --version
```

#### 2. 克隆项目

```cmd
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert\basketball_training_system
```

如果没有git，可以直接下载ZIP文件并解压。

#### 3. 创建虚拟环境（推荐）

```cmd
python -m venv venv
venv\Scripts\activate
```

#### 4. 安装依赖

```cmd
pip install -r requirements.txt
```

如果遇到网络问题，可以使用国内镜像:
```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 5. 启动系统

```cmd
python run.py
```

### Linux系统 (Ubuntu/Debian)

#### 1. 更新系统并安装Python

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

#### 2. 克隆项目

```bash
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert/basketball_training_system
```

#### 3. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. 安装依赖

```bash
pip install -r requirements.txt
```

#### 5. 启动系统

```bash
python run.py
```

### macOS系统

#### 1. 安装Homebrew（如果没有）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. 安装Python

```bash
brew install python@3.10
```

#### 3. 克隆项目

```bash
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert/basketball_training_system
```

#### 4. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 5. 安装依赖

```bash
pip install -r requirements.txt
```

#### 6. 启动系统

```bash
python run.py
```

## 依赖项说明

### 核心依赖
- **torch**: PyTorch深度学习框架
- **ultralytics**: YOLOv8官方实现
- **opencv-python**: 图像处理库
- **Flask**: Web框架
- **numpy**: 数值计算库

### 可选依赖
如果需要GPU加速，安装CUDA版本的PyTorch:

```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## 常见安装问题

### 问题1: pip安装超时

**解决方案**: 使用国内镜像源

```bash
# 临时使用
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置（推荐）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2: OpenCV安装失败

**解决方案**: 

Windows:
```cmd
pip install opencv-python-headless
```

Linux:
```bash
sudo apt install libgl1-mesa-glx
pip install opencv-python
```

### 问题3: PyTorch安装失败

**解决方案**: 访问 [PyTorch官网](https://pytorch.org/get-started/locally/) 获取适合你系统的安装命令。

### 问题4: 权限错误 (Linux/Mac)

**解决方案**: 
```bash
# 不要使用sudo安装，而是使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 问题5: Microsoft Visual C++ 错误 (Windows)

**解决方案**: 下载并安装 [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

## 验证安装

运行测试脚本验证所有组件是否正常:

```bash
python example_usage.py
```

如果看到以下输出，说明安装成功:
```
🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀
YOLOv8篮球训练辅助系统 - 使用示例
🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀🏀
...
✓ 所有示例运行完成！
```

## GPU加速配置

### NVIDIA GPU用户

1. 检查CUDA版本:
```bash
nvidia-smi
```

2. 安装对应版本的PyTorch:
```bash
# 根据CUDA版本选择
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

3. 修改配置文件 `configs/config.yaml`:
```yaml
model:
  yolo:
    device: "cuda"
  pose:
    device: "cuda"
```

4. 验证GPU是否可用:
```python
import torch
print(torch.cuda.is_available())  # 应该输出 True
print(torch.cuda.get_device_name(0))  # 显示GPU名称
```

## Docker安装（高级用户）

创建 `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "run.py"]
```

构建和运行:
```bash
docker build -t basketball-training .
docker run -p 5000:5000 basketball-training
```

## 更新系统

```bash
# 进入项目目录
cd basketball_training_system

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启系统
python run.py
```

## 卸载

```bash
# 删除虚拟环境
rm -rf venv

# 删除项目文件
cd ..
rm -rf basketball_training_system
```

## 获取帮助

如果遇到安装问题:
1. 查看错误日志
2. 搜索相关错误信息
3. 提交Issue到GitHub
4. 联系作者: 2057680774@qq.com

---

**注意**: 首次运行时，系统会自动下载YOLOv8模型文件（约6MB），请确保网络连接正常。
