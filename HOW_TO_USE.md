# 🎯 如何使用这个系统

## 最快速的回答

### 第一次使用？看这里 👇

```bash
# 1. 克隆项目
git clone https://github.com/EmmasAlbert/EmmasAlbert.git
cd EmmasAlbert

# 2. 启动系统（只需这一步！）
docker-compose up -d

# 3. 打开浏览器访问
http://localhost:3000
```

**就这么简单！** 系统已经运行了 ✅

---

## 根据你的身份，选择相应的使用指南

### 👨‍🎓 我是学生

**目标**：上传视频，查看分析结果，提高篮球技能

**你需要看**：
1. [用户使用指南 - 学生章节](docs/USER_GUIDE_CN.md#学生用户)
   - 如何注册账号
   - 如何上传训练视频
   - 如何查看AI分析结果
   - 如何查看个人数据
   - 如何学习课程

**快速操作**：
```
访问系统 → 注册 → 登录 → 上传视频 → 等待分析 → 查看结果
```

---

### 👨‍🏫 我是教练

**目标**：管理学生，制定训练计划，查看学生进度

**你需要看**：
1. [用户使用指南 - 教练章节](docs/USER_GUIDE_CN.md#教练用户)
   - 如何创建班级
   - 如何管理学生
   - 如何制定训练计划
   - 如何布置作业
   - 如何点评学生

**快速操作**：
```
注册教练账号 → 创建班级 → 邀请学生 → 查看学生数据 → 制定计划
```

---

### 👨‍💼 我是管理员

**目标**：部署系统，管理用户，维护运行

**你需要看**：
1. [安装部署指南](docs/INSTALLATION.md) - 如何部署
2. [用户使用指南 - 管理员章节](docs/USER_GUIDE_CN.md#管理员用户) - 如何管理
3. [快速参考手册](docs/QUICK_REFERENCE.md) - 运维命令

**快速操作**：
```
部署系统 → 配置数据库 → 创建管理员账号 → 系统监控 → 用户管理
```

---

### 👨‍💻 我是开发者

**目标**：了解系统架构，开发新功能

**你需要看**：
1. [系统架构文档](docs/SYSTEM_ARCHITECTURE.md)
2. [模块设计文档](docs/MODULE_DESIGN.md)
3. [API使用指南](docs/API_GUIDE.md)

**快速操作**：
```
了解架构 → 本地部署 → 阅读代码 → 开发功能 → 测试 → 提交PR
```

---

### 🤖 我想训练AI模型

**目标**：用自己的数据训练YOLOv8模型

**你需要看**：
1. [YOLOv8训练指南（中文）](docs/YOLOV8_TRAINING_GUIDE_CN.md) ⭐ 推荐
2. [训练快速示例](docs/YOLOV8_TRAINING_EXAMPLE.md)

**快速操作**：
```bash
# 1. 准备数据集（YOLO格式）
# 2. 配置 ai_engine/training/dataset_config.yaml
# 3. 开始训练
cd ai_engine/training
python train_yolov8.py --config dataset_config.yaml --model s --epochs 100
```

---

## 📚 完整文档列表

不知道看哪个文档？查看 **[文档导航](docs/DOCUMENTATION_INDEX.md)**

### 最重要的3个文档

1. **[用户使用指南（中文）](docs/USER_GUIDE_CN.md)** ⭐⭐⭐⭐⭐
   - 12,000字完整教程
   - 按角色详细说明
   - 包含常见问题

2. **[快速参考手册](docs/QUICK_REFERENCE.md)** ⭐⭐⭐⭐
   - 9,000字速查表
   - 常用命令
   - 故障排查

3. **[文档导航](docs/DOCUMENTATION_INDEX.md)** ⭐⭐⭐⭐
   - 帮你找到合适的文档
   - 20+文档索引

---

## ❓ 遇到问题？

### 1. 先看常见问题
[用户指南 - 常见问题](docs/USER_GUIDE_CN.md#常见问题) 包含了15个最常见的问题

### 2. 搜索GitHub Issues
可能别人也遇到过相同问题：
https://github.com/EmmasAlbert/EmmasAlbert/issues

### 3. 联系技术支持
- 📧 邮箱：2057680774@qq.com
- 💬 QQ/微信：2057680774
- 🐛 提交Issue：https://github.com/EmmasAlbert/EmmasAlbert/issues/new

---

## 🎯 快速场景指南

### 场景1：我想分析投篮视频

```
1. 访问 http://localhost:3000
2. 注册/登录
3. 进入「训练管理」→「视频分析」
4. 上传视频
5. 等待AI分析（5-10分钟）
6. 查看分析结果
```

详细说明：[视频上传和分析](docs/USER_GUIDE_CN.md#视频上传和分析)

### 场景2：我想实时训练

```
1. 登录系统
2. 进入「训练管理」→「实时训练」
3. 允许摄像头权限
4. 调整摄像头角度
5. 开始训练
6. 获得实时反馈
```

详细说明：[实时训练模式](docs/USER_GUIDE_CN.md#实时训练模式)

### 场景3：我想查看我的进步

```
1. 登录系统
2. 进入「数据分析」
3. 查看统计图表
   - 命中率趋势
   - 训练频率
   - 姿态得分
4. 导出报告（可选）
```

详细说明：[数据统计和可视化](docs/USER_GUIDE_CN.md#数据统计和可视化)

### 场景4：教练想管理班级

```
1. 注册/登录教练账号
2. 创建班级
3. 获取邀请码，分享给学生
4. 学生加入后：
   - 查看学生数据
   - 制定训练计划
   - 点评学生表现
```

详细说明：[教练用户](docs/USER_GUIDE_CN.md#教练用户)

---

## 💡 使用技巧

### 1. 提高AI分析准确度
- ✅ 保证光线充足
- ✅ 背景简单
- ✅ 摄像头稳定
- ✅ 完整拍摄动作

### 2. 提高命中率
- ✅ 认真查看AI分析
- ✅ 关注姿态评分
- ✅ 按建议改进
- ✅ 持续练习

### 3. 充分利用系统
- ✅ 每天训练并记录
- ✅ 完成系统课程
- ✅ 参与排行榜
- ✅ 向教练请教

---

## 🚀 下一步做什么？

### 新用户
1. ✅ 启动系统
2. ✅ 注册账号
3. ✅ 上传第一个视频
4. ⏭️ 查看更多功能
5. ⏭️ 学习在线课程

### 活跃用户
1. ✅ 定期训练
2. ✅ 跟踪进步
3. ⏭️ 参加挑战
4. ⏭️ 解锁成就
5. ⏭️ 冲击排行榜

### 教练用户
1. ✅ 创建班级
2. ✅ 添加学生
3. ⏭️ 制定计划
4. ⏭️ 发布课程
5. ⏭️ 分析数据

---

## 📱 支持的设备

- 💻 电脑（Windows/Mac/Linux）
- 📱 手机（iOS/Android）
- 📱 平板（iPad/Android平板）
- 推荐使用Chrome或Edge浏览器

---

## 🎉 开始使用吧！

**最简单的开始方式**：

```bash
docker-compose up -d
```

然后打开浏览器访问 http://localhost:3000

**就这么简单！享受智能篮球训练吧！** 🏀✨

---

<p align="center">
  <img src="416.png" width="100" />
</p>

<p align="center">
  <strong>祝你训练愉快，篮球技术越来越好！</strong>
</p>

<p align="center">
  有问题？查看 <a href="docs/USER_GUIDE_CN.md">完整使用指南</a> 或 <a href="docs/DOCUMENTATION_INDEX.md">文档导航</a>
</p>
