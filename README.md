# 🤖 Pipecat 语音助手 Demo - SIP 版本

一个基于 [Pipecat](https://github.com/pipecat-ai/pipecat) 框架的实时 SIP 语音对话 AI 助手演示项目。

## ✨ 功能特性

- 🧠 **Google Gemini 2.0 Flash Lite**：快速响应的 AI 对话模型
- 🎤 **Deepgram Nova 2**：先进的实时语音识别
- 🔊 **ElevenLabs TTS**：支持印度口音英语的自然语音合成
- 📞 **Twilio SIP**：支持通过自己的 SIP 线路落地
- ⚡ **低延迟**：基于 WebSocket 实现实时音频流传输
- 🔄 **并发支持**：可同时处理多个通话

## 📋 前置要求

在开始之前，你需要准备：

1. **Python 3.9+**

2. **Google Gemini API 密钥**
   - 获取地址：https://makersuite.google.com/app/apikey

3. **Deepgram API 密钥**
   - 注册地址：https://console.deepgram.com/
   - 提供免费额度用于测试

4. **ElevenLabs API 密钥**
   - 注册地址：https://elevenlabs.io/
   - 获取地址：https://elevenlabs.io/app/settings/api-keys

5. **Twilio 账户**
   - 注册地址：https://www.twilio.com/try-twilio
   - 需要 Account SID、Auth Token 和电话号码

6. **公网访问**
   - 使用 ngrok 或拥有公网 IP 的服务器
   - Twilio webhook 需要 HTTPS

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
# AI 服务密钥
GEMINI_API_KEY=your_gemini_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Twilio 配置
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# 服务器配置
HOST=0.0.0.0
PORT=7860
PUBLIC_URL=https://your-domain.com  # 或 ngrok URL
```

### 4. 设置公网访问（本地开发）

如果在本地开发，使用 ngrok：

```bash
# 安装 ngrok
# 下载地址: https://ngrok.com/download

# 启动 ngrok
ngrok http 7860
```

将 ngrok 提供的 HTTPS URL（如 `https://abc123.ngrok.io`）设置为 `PUBLIC_URL`。

### 5. 配置 Twilio Webhook

1. 访问 [Twilio Console](https://console.twilio.com/)
2. 进入 Phone Numbers → Manage → Active numbers
3. 选择你的电话号码
4. 在 "Voice Configuration" 部分：
   - **A CALL COMES IN**: 选择 `Webhook`，填入 `https://your-domain.com/incoming-call`，选择 `HTTP POST`
   - **STATUS CALLBACK URL**: 填入 `https://your-domain.com/call-status`，选择 `HTTP POST`
5. 保存配置

详细的 Twilio 配置说明请参考 [TWILIO_SETUP.md](TWILIO_SETUP.md)

### 6. 启动服务器

```bash
python server.py
```

你会看到类似输出：

```
============================================================
🚀 Pipecat 语音助手服务器 - SIP 版本
============================================================
📍 服务器地址: http://0.0.0.0:7860

📋 技术栈:
   🧠 模型: Gemini 2.0 Flash Lite
   🎤 ASR: Deepgram Nova 2
   🔊 TTS: ElevenLabs (印度口音)
   📞 Telephony: Twilio SIP

🔗 Webhook 端点:
   - 来电: http://0.0.0.0:7860/incoming-call
   - 状态: http://0.0.0.0:7860/call-status

💡 请在 Twilio 控制台配置这些 webhook URL
============================================================
```

### 7. 测试通话

拨打你配置的 Twilio 电话号码，应该会听到 AI 助手用印度口音英语问候你！

## 📖 使用说明

### 基本使用

1. **拨打电话**
   - 使用任何电话拨打你的 Twilio 号码
   - 等待 AI 助手接听并问候

2. **与助手对话**
   - AI 会自动检测你何时说完话
   - 用自然语言提问或聊天
   - 助手会用印度口音英语回答

3. **结束通话**
   - 直接挂断电话即可
   - 系统会自动清理资源

### API 端点

查看服务状态：
```bash
curl http://localhost:7860/api/health
```

查看活跃通话：
```bash
curl http://localhost:7860/api/active-calls
```

手动挂断通话：
```bash
curl -X POST http://localhost:7860/api/hangup/{call_sid}
```

## 🏗️ 项目结构

```
VoiceAgentByPipecat/
├── bot.py              # 语音助手核心逻辑（Gemini + Deepgram + ElevenLabs）
├── server.py           # FastAPI Web 服务器（Twilio webhook 处理）
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量示例
├── .gitignore          # Git 忽略文件
├── README.md           # 项目说明（本文件）
├── TWILIO_SETUP.md     # Twilio 详细配置指南
└── index.html          # 前端界面（可选）
```

## 🔧 核心组件说明

### bot.py
- 使用 Pipecat 框架构建的 SIP 语音对话机器人
- 集成 Google Gemini 2.0 Flash Lite 作为对话模型
- 使用 Deepgram Nova 2 进行语音转文本
- 使用 ElevenLabs 进行文本转语音（印度口音）
- 通过 Twilio 处理 SIP 通话

### server.py
- FastAPI Web 服务器
- 处理 Twilio webhook（来电、状态回调）
- 管理 bot 进程的生命周期
- 提供监控 API 端点

### 处理流程

```
来电 → Twilio → Webhook (/incoming-call)
                    ↓
                启动 Bot 进程
                    ↓
            音频流 WebSocket
                    ↓
        Deepgram (语音→文字)
                    ↓
        Gemini (AI 对话处理)
                    ↓
        ElevenLabs (文字→语音)
                    ↓
            返回音频到通话
```

## 🎯 技术栈

- **Pipecat AI**: 语音对话框架
- **Google Gemini 2.0 Flash Lite**: 快速高效的 LLM
- **Deepgram Nova 2**: 实时语音识别
- **ElevenLabs**: 高质量语音合成（印度口音）
- **Twilio**: SIP 电话服务
- **FastAPI**: Python Web 框架

## ⚙️ 高级配置

### 修改 AI 助手的性格

编辑 `bot.py` 中的系统提示：

```python
system_prompt = """You are a friendly AI voice assistant...
在这里修改助手的性格、语言风格等
"""
```

### 更换 ElevenLabs 语音

查看可用语音：https://elevenlabs.io/app/voice-library

在 `.env` 文件中设置：

```env
ELEVENLABS_VOICE_ID=your_preferred_voice_id
```

或修改 `bot.py` 中的 `voice_id` 参数。

### 调整语音参数

在 `bot.py` 中修改 TTS 配置：

```python
tts = ElevenLabsTTSService(
    api_key=elevenlabs_api_key,
    voice_id="pNInz6obpgDQGcFmaJgB",
    model_id="eleven_multilingual_v2",
    stability=0.5,          # 稳定性 (0-1)
    similarity_boost=0.75,  # 相似度提升 (0-1)
)
```

### 使用自己的 SIP 线路

如果你想使用自己的 SIP 提供商而不是 Twilio 电话号码：

1. 配置 Twilio SIP Trunking
2. 连接你的 SIP 提供商
3. 详细步骤参考 [TWILIO_SETUP.md](TWILIO_SETUP.md)

### 更换 Gemini 模型

在 `bot.py` 中修改：

```python
llm = GoogleLLMService(
    api_key=gemini_api_key,
    model="gemini-2.0-flash-exp",  # 或其他 Gemini 模型
)
```

可用模型：
- `gemini-2.0-flash-exp` - Gemini 2.0 Flash (实验版)
- `gemini-1.5-pro` - Gemini 1.5 Pro
- `gemini-1.5-flash` - Gemini 1.5 Flash

## 🐛 常见问题

### 1. 安装依赖失败

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Twilio webhook 无法访问

确保：
- `PUBLIC_URL` 是公网可访问的 HTTPS URL
- 如使用 ngrok，确保它正在运行
- 检查防火墙设置

### 3. 通话无声音

检查：
- 所有 API 密钥是否正确
- 查看服务器日志确认 bot 是否启动
- 确认 Deepgram 和 ElevenLabs API 配额充足
- 查看 Twilio 控制台的 Debug Logs

### 4. Bot 未启动

确认：
- `.env` 文件中所有必需变量都已设置
- 手动运行 `python bot.py` 测试
- 检查服务器日志

### 5. ElevenLabs 语音不是印度口音

在 ElevenLabs Voice Library 中：
1. 搜索 "Indian" 或 "Indian English"
2. 选择合适的语音
3. 复制 Voice ID
4. 更新 `.env` 文件中的 `ELEVENLABS_VOICE_ID`

## 📝 开发说明

### 本地开发

```bash
# 启动开发服务器（自动重载）
uvicorn server:app --reload --host 0.0.0.0 --port 7860
```

### 日志调试

修改 `bot.py` 或 `server.py` 中的日志级别：

```python
logger.add(sys.stderr, level="DEBUG")  # 显示详细日志
```

### 测试 Webhook

使用 curl 测试：

```bash
# 测试来电 webhook
curl -X POST http://localhost:7860/incoming-call

# 测试健康检查
curl http://localhost:7860/api/health
```

## 🚀 生产部署

### 推荐配置

1. **使用云服务器**（AWS, GCP, DigitalOcean 等）
2. **配置 Nginx 反向代理**
3. **使用 SSL 证书**（Let's Encrypt）
4. **使用进程管理器**（systemd, supervisor）
5. **设置日志轮转**
6. **配置监控告警**

### 示例 systemd 服务

创建 `/etc/systemd/system/pipecat-voice.service`：

```ini
[Unit]
Description=Pipecat Voice Assistant
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/VoiceAgentByPipecat
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable pipecat-voice
sudo systemctl start pipecat-voice
```

## 💰 成本估算

各服务的大致成本（2024年价格）：

- **Gemini API**: 免费额度 + 按使用付费
- **Deepgram**: $0.0043/分钟（按量付费）
- **ElevenLabs**: 免费额度 10,000 字符/月，付费 $5/月起
- **Twilio**: 入站通话约 $0.0085/分钟，出站略贵

每分钟通话总成本约 $0.01 - $0.02（不含 LLM）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Pipecat 官方文档](https://docs.pipecat.ai/)
- [Google Gemini API](https://ai.google.dev/)
- [Deepgram 文档](https://developers.deepgram.com/)
- [ElevenLabs 文档](https://elevenlabs.io/docs/)
- [Twilio 文档](https://www.twilio.com/docs)

## 📞 技术支持

如有问题：
1. 查看 [TWILIO_SETUP.md](TWILIO_SETUP.md) 获取详细配置说明
2. 检查项目 Issues
3. 查看各服务商的文档和状态页面

---

**祝你使用愉快！如有问题，欢迎提 Issue。** 🎉
