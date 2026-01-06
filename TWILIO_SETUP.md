# Twilio SIP 配置指南

本文档说明如何配置 Twilio 以使用你自己的 SIP 线路与 Pipecat 语音助手集成。

## 📋 前置条件

1. Twilio 账户（免费或付费）
2. 一个公网可访问的服务器 URL（使用 ngrok 或你的域名）
3. 你自己的 SIP 线路（可选，如果使用 Twilio 电话号码则不需要）

## 🚀 快速开始

### 1. 获取 Twilio 凭证

登录 [Twilio Console](https://console.twilio.com/)，获取：

- **Account SID**：在控制台首页可以找到
- **Auth Token**：点击 "Show" 按钮查看
- **电话号码**：购买或使用现有的 Twilio 电话号码

### 2. 配置环境变量

在 `.env` 文件中设置：

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
PUBLIC_URL=https://your-domain.com
```

### 3. 暴露本地服务器到公网

如果你在本地开发，使用 ngrok：

```bash
# 安装 ngrok (如果还没有)
# 下载地址: https://ngrok.com/download

# 启动 ngrok
ngrok http 7860
```

ngrok 会给你一个公网 URL，例如 `https://abc123.ngrok.io`

将这个 URL 设置为 `PUBLIC_URL` 环境变量。

### 4. 配置 Twilio Webhook

1. 访问 [Twilio Phone Numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. 选择你的电话号码
3. 在 "Voice & Fax" 部分：
   - **A CALL COMES IN**: 设置为 `Webhook`
   - **URL**: `https://your-domain.com/incoming-call`
   - **HTTP**: 选择 `POST`

4. 在 "Status Callback URL" 部分：
   - **URL**: `https://your-domain.com/call-status`
   - **HTTP**: 选择 `POST`

5. 点击 "Save" 保存配置

## 📞 使用自己的 SIP 线路

如果你想使用自己的 SIP 线路而不是 Twilio 电话号码：

### 方案 1: Twilio SIP Trunking

1. 访问 [Twilio Elastic SIP Trunking](https://console.twilio.com/us1/develop/sip-trunking/trunks)
2. 创建一个新的 Trunk
3. 配置 Origination URI（你的 SIP 提供商地址）
4. 配置 Termination URI（指向你的服务器）
5. 设置 Webhook URL 为你的服务器端点

### 方案 2: 直接 SIP 集成

如果你想完全绕过 Twilio，直接使用 SIP：

1. 修改 `bot.py` 中的 transport 配置
2. 使用 Pipecat 的其他 SIP transport（如 FreeSWITCH 或 Asterisk）
3. 配置你的 SIP 服务器转发音频流到 bot

**示例配置**（需要修改 bot.py）:

```python
# 替换 TwilioTransport 为直接 SIP transport
# 注意: 这需要额外的配置和 SIP 服务器设置

from pipecat.transports.sip import SIPTransport

transport = SIPTransport(
    sip_server="your-sip-server.com",
    sip_port=5060,
    username="your-sip-username",
    password="your-sip-password",
)
```

## 🧪 测试配置

### 1. 启动服务器

```bash
python server.py
```

你应该看到：

```
🚀 Pipecat 语音助手服务器 - SIP 版本
📍 服务器地址: http://0.0.0.0:7860
...
🔗 Webhook 端点:
   - 来电: http://0.0.0.0:7860/incoming-call
   - 状态: http://0.0.0.0:7860/call-status
```

### 2. 测试 Webhook

使用 curl 测试来电 webhook：

```bash
curl -X POST https://your-domain.com/incoming-call
```

应该返回 TwiML XML 响应。

### 3. 拨打测试电话

拨打你配置的 Twilio 电话号码，应该听到 AI 助手的问候。

## 🔧 故障排查

### Webhook 无法访问

**问题**: Twilio 无法访问你的 webhook URL

**解决方案**:
1. 确保 `PUBLIC_URL` 是公网可访问的
2. 检查防火墙设置
3. 使用 ngrok 时确保它正在运行
4. 检查 webhook URL 是否正确配置

### 通话无声音

**问题**: 电话接通了但听不到声音

**解决方案**:
1. 检查所有 API 密钥是否正确配置
2. 查看服务器日志确认 bot 是否启动
3. 确认 Deepgram 和 ElevenLabs 服务正常
4. 检查 Twilio 控制台的 Debug Logs

### Bot 未启动

**问题**: 来电时 bot 进程没有启动

**解决方案**:
1. 检查服务器日志
2. 确认 `.env` 文件中所有必需变量都已设置
3. 手动运行 `python bot.py` 测试
4. 检查 Python 依赖是否完整安装

## 📊 监控通话

### API 端点

查看活跃通话：
```bash
curl https://your-domain.com/api/active-calls
```

健康检查：
```bash
curl https://your-domain.com/api/health
```

手动挂断通话：
```bash
curl -X POST https://your-domain.com/api/hangup/{call_sid}
```

## 🔐 安全建议

1. **保护你的凭证**
   - 永远不要提交 `.env` 文件到 Git
   - 使用环境变量管理敏感信息
   - 定期轮换 API 密钥

2. **使用 HTTPS**
   - Twilio webhook 必须使用 HTTPS
   - 生产环境中配置 SSL 证书
   - 使用 Let's Encrypt 获取免费证书

3. **验证 Webhook**
   - 验证 Twilio webhook 签名
   - 只接受来自 Twilio IP 的请求

4. **限制访问**
   - 设置 IP 白名单
   - 使用 API 密钥认证
   - 实施速率限制

## 🌐 生产部署

推荐的生产环境配置：

1. **使用云服务器**
   - AWS EC2, Google Cloud, DigitalOcean 等
   - 配置固定的公网 IP 和域名

2. **配置反向代理**
   - 使用 Nginx 或 Caddy
   - 配置 SSL 证书
   - 设置适当的超时时间

3. **进程管理**
   - 使用 systemd 或 supervisor
   - 配置自动重启
   - 设置日志轮转

4. **监控和告警**
   - 设置健康检查
   - 配置日志收集
   - 设置性能监控

示例 Nginx 配置：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📚 相关资源

- [Twilio 官方文档](https://www.twilio.com/docs)
- [Twilio Webhook 指南](https://www.twilio.com/docs/usage/webhooks)
- [Twilio TwiML 文档](https://www.twilio.com/docs/voice/twiml)
- [Twilio SIP Trunking](https://www.twilio.com/docs/sip-trunking)
- [Pipecat 文档](https://docs.pipecat.ai/)

## ❓ 常见问题

**Q: 需要付费的 Twilio 账户吗？**

A: 免费试用账户可以用于开发测试，但生产环境建议升级到付费账户。

**Q: 可以使用其他 SIP 提供商吗？**

A: 可以！通过 Twilio SIP Trunking 或直接 SIP 集成都可以。

**Q: 通话费用如何计算？**

A: 查看 [Twilio 定价页面](https://www.twilio.com/voice/pricing) 了解详情。

**Q: 支持并发多个通话吗？**

A: 支持！服务器会为每个来电创建独立的 bot 实例。

---

如有问题，请查看项目 Issues 或联系技术支持。
