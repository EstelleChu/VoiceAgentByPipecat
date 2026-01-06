# 🤖 Pipecat 语音助手 Demo

一个基于 [Pipecat](https://github.com/pipecat-ai/pipecat) 框架的实时语音对话 AI 助手演示项目。

## ✨ 功能特性

- 🎤 **实时语音对话**：通过麦克风与 AI 助手进行自然对话
- 🧠 **智能对话**：集成 OpenAI GPT-4 提供智能回复
- 🔊 **语音合成**：使用 OpenAI TTS 将文本转换为自然语音
- 🌐 **Web 界面**：简洁美观的浏览器界面，无需安装客户端
- ⚡ **低延迟**：基于 WebRTC 实现实时音频传输

## 📋 前置要求

在开始之前，你需要准备：

1. **Python 3.9+**
2. **OpenAI API 密钥**
   - 注册地址：https://platform.openai.com/
   - 获取 API Key：https://platform.openai.com/api-keys
3. **Daily.co API 密钥**
   - 注册地址：https://www.daily.co/
   - 获取 API Key：https://dashboard.daily.co/developers

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd VoiceAgentByPipecat
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 文件为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 密钥：

```env
# OpenAI API 密钥
OPENAI_API_KEY=sk-your-openai-api-key-here

# Daily.co API 密钥
DAILY_API_KEY=your-daily-api-key-here

# 服务器配置（可选）
HOST=0.0.0.0
PORT=7860
```

### 4. 启动服务器

```bash
python server.py
```

你会看到类似输出：

```
🚀 启动服务器: http://0.0.0.0:7860
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
```

### 5. 打开浏览器

访问 http://localhost:7860 即可开始使用！

## 📖 使用说明

1. **启动对话**
   - 点击页面上的 "🎤 开始对话" 按钮
   - 允许浏览器访问你的麦克风
   - 等待几秒钟，系统会自动创建房间并启动 AI 助手

2. **与助手对话**
   - AI 助手会主动问候你
   - 直接对着麦克风说话即可
   - AI 会自动检测你何时说完，然后给出回应

3. **结束对话**
   - 点击 "⏹️ 结束对话" 按钮
   - 系统会自动清理资源

## 🏗️ 项目结构

```
VoiceAgentByPipecat/
├── bot.py              # 语音助手核心逻辑
├── server.py           # FastAPI Web 服务器
├── index.html          # 前端界面
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量示例
└── README.md           # 项目说明
```

## 🔧 核心组件说明

### bot.py
- 使用 Pipecat 框架构建的语音对话机器人
- 集成 OpenAI GPT-4 作为对话模型
- 使用 Daily.co 作为 WebRTC 传输层
- 支持语音活动检测（VAD）

### server.py
- FastAPI Web 服务器
- 管理 Daily.co 房间的创建
- 启动和管理 bot 进程
- 提供 REST API 端点

### index.html
- 用户友好的 Web 界面
- 集成 Daily.co JavaScript SDK
- 实时状态显示和错误处理

## 🎯 技术栈

- **Pipecat AI**: 语音对话框架
- **OpenAI**: GPT-4 对话模型 + TTS 语音合成
- **Daily.co**: WebRTC 实时通信
- **FastAPI**: Python Web 框架
- **Silero VAD**: 语音活动检测

## ⚙️ 高级配置

### 修改 AI 助手的性格

编辑 `bot.py` 中的系统提示（system prompt）：

```python
context = OpenAILLMContext(
    messages=[
        {
            "role": "system",
            "content": "在这里修改助手的性格和行为..."
        }
    ]
)
```

### 更换语言模型

在 `bot.py` 中修改：

```python
llm = OpenAILLMService(
    api_key=openai_api_key,
    model="gpt-4"  # 可改为 gpt-3.5-turbo 等
)
```

### 修改服务器端口

在 `.env` 文件中设置：

```env
PORT=8000  # 改为你想要的端口
```

## 🐛 常见问题

### 1. 安装依赖失败

如果遇到依赖安装问题，尝试：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 找不到 OpenAI API 密钥

确保：
- `.env` 文件存在且格式正确
- `OPENAI_API_KEY` 变量已设置
- API 密钥有效且有足够额度

### 3. Daily.co 连接失败

检查：
- `DAILY_API_KEY` 是否正确
- 网络连接是否正常
- 浏览器是否允许麦克风权限

### 4. 语音无法识别

确认：
- 麦克风正常工作
- 浏览器已授予麦克风权限
- 网络延迟较低

## 📝 开发说明

### 本地开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器（自动重载）
uvicorn server:app --reload --host 0.0.0.0 --port 7860
```

### 日志调试

修改 `bot.py` 中的日志级别：

```python
logger.add(sys.stderr, level="DEBUG")  # 显示详细日志
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Pipecat 官方文档](https://docs.pipecat.ai/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Daily.co 开发者文档](https://docs.daily.co/)

---

**祝你使用愉快！如有问题，欢迎提 Issue。** 🎉
