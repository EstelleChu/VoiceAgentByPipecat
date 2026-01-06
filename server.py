"""
FastAPI 服务器 - Twilio SIP 版本
管理通过 Twilio 的 SIP 语音对话会话
"""

import os
import sys
import asyncio
import subprocess
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from loguru import logger

# 加载环境变量
load_dotenv()

# 配置日志
logger.remove(0)
logger.add(sys.stderr, level="INFO")

# 创建 FastAPI 应用
app = FastAPI(title="Pipecat 语音助手 Demo - SIP 版本")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
bot_processes = {}  # 存储运行中的 bot 进程


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页 HTML - SIP 版本"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="""
            <h1>Pipecat 语音助手 - SIP 版本</h1>
            <p>这是一个通过 Twilio SIP 线路的语音助手演示。</p>
            <h2>技术栈：</h2>
            <ul>
                <li>🧠 模型: Google Gemini 2.0 Flash Lite</li>
                <li>🎤 ASR: Deepgram Nova 2</li>
                <li>🔊 TTS: ElevenLabs (印度口音英语)</li>
                <li>📞 Telephony: Twilio SIP</li>
            </ul>
            <h2>配置说明：</h2>
            <p>请查看 README.md 了解如何配置 Twilio webhook。</p>
            """,
            status_code=200
        )


@app.post("/incoming-call")
async def handle_incoming_call(request: Request):
    """
    处理 Twilio 来电 webhook
    当有电话打入时，Twilio 会调用这个端点
    """
    logger.info("📞 收到来电")

    # 获取服务器配置
    host = os.getenv("HOST", "0.0.0.0")
    port = os.getenv("PORT", 7860)
    public_url = os.getenv("PUBLIC_URL", f"http://{host}:{port}")

    # 创建 TwiML 响应
    response = VoiceResponse()

    # 连接到 WebSocket 流
    connect = Connect()
    stream = Stream(url=f"{public_url}/media-stream")
    connect.append(stream)
    response.append(connect)

    logger.info(f"TwiML 响应: {str(response)}")

    return Response(content=str(response), media_type="application/xml")


@app.api_route("/media-stream", methods=["GET", "POST"])
async def handle_media_stream(request: Request):
    """
    处理 Twilio 媒体流 WebSocket
    这里启动 bot 来处理音频流
    """
    logger.info("🎵 媒体流连接")

    # 获取通话信息
    form_data = await request.form()
    call_sid = form_data.get("CallSid")

    if call_sid and call_sid not in bot_processes:
        # 启动 bot 进程
        logger.info(f"🤖 为通话 {call_sid} 启动 bot")

        try:
            # 获取 Twilio 配置
            twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

            if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
                logger.error("❌ 缺少 Twilio 配置")
                raise HTTPException(status_code=500, detail="缺少 Twilio 配置")

            # 启动 bot 进程
            bot_process = subprocess.Popen(
                [sys.executable, "bot.py", call_sid],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 存储进程信息
            bot_processes[call_sid] = {
                "process": bot_process,
                "call_sid": call_sid,
                "started_at": datetime.now().isoformat()
            }

            logger.info(f"✅ Bot 已启动: {call_sid}")

        except Exception as e:
            logger.error(f"❌ 启动 bot 失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"启动 bot 失败: {str(e)}")

    return Response(content="", media_type="text/plain")


@app.post("/call-status")
async def handle_call_status(request: Request):
    """
    处理通话状态 webhook
    当通话状态改变时，Twilio 会调用这个端点
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")

    logger.info(f"📞 通话状态更新: {call_sid} - {call_status}")

    # 如果通话结束，清理 bot 进程
    if call_status in ["completed", "failed", "busy", "no-answer"]:
        if call_sid in bot_processes:
            try:
                bot_info = bot_processes[call_sid]
                process = bot_info["process"]
                process.terminate()
                process.wait(timeout=5)
                del bot_processes[call_sid]
                logger.info(f"✅ Bot 已清理: {call_sid}")
            except Exception as e:
                logger.error(f"❌ 清理 bot 失败: {str(e)}")

    return Response(content="", media_type="text/plain")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return JSONResponse({
        "status": "healthy",
        "active_bots": len(bot_processes),
        "timestamp": datetime.now().isoformat(),
        "config": {
            "model": "Gemini 2.0 Flash Lite",
            "asr": "Deepgram Nova 2",
            "tts": "ElevenLabs (印度口音)",
            "telephony": "Twilio SIP"
        }
    })


@app.get("/api/active-calls")
async def get_active_calls():
    """获取当前活跃的通话列表"""
    calls = []
    for call_sid, bot_info in bot_processes.items():
        calls.append({
            "call_sid": call_sid,
            "started_at": bot_info["started_at"],
            "status": "active"
        })

    return JSONResponse({
        "count": len(calls),
        "calls": calls
    })


@app.post("/api/hangup/{call_sid}")
async def hangup_call(call_sid: str):
    """手动挂断指定的通话"""
    if call_sid not in bot_processes:
        raise HTTPException(status_code=404, detail="未找到该通话")

    try:
        bot_info = bot_processes[call_sid]
        process = bot_info["process"]

        # 终止进程
        process.terminate()
        process.wait(timeout=5)

        # 删除记录
        del bot_processes[call_sid]

        logger.info(f"✅ 通话已挂断: {call_sid}")

        return JSONResponse({
            "success": True,
            "message": f"通话已挂断: {call_sid}"
        })

    except Exception as e:
        logger.error(f"❌ 挂断失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"挂断失败: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理所有 bot 进程"""
    logger.info("🛑 正在关闭服务器，清理资源...")

    for call_sid, bot_info in bot_processes.items():
        try:
            process = bot_info["process"]
            process.terminate()
            process.wait(timeout=5)
            logger.info(f"✅ 已停止 bot: {call_sid}")
        except Exception as e:
            logger.error(f"❌ 清理 bot 失败 {call_sid}: {e}")


if __name__ == "__main__":
    import uvicorn

    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 7860))

    logger.info("=" * 60)
    logger.info("🚀 Pipecat 语音助手服务器 - SIP 版本")
    logger.info("=" * 60)
    logger.info(f"📍 服务器地址: http://{host}:{port}")
    logger.info("")
    logger.info("📋 技术栈:")
    logger.info("   🧠 模型: Gemini 2.0 Flash Lite")
    logger.info("   🎤 ASR: Deepgram Nova 2")
    logger.info("   🔊 TTS: ElevenLabs (印度口音)")
    logger.info("   📞 Telephony: Twilio SIP")
    logger.info("")
    logger.info("🔗 Webhook 端点:")
    logger.info(f"   - 来电: http://{host}:{port}/incoming-call")
    logger.info(f"   - 状态: http://{host}:{port}/call-status")
    logger.info("")
    logger.info("💡 请在 Twilio 控制台配置这些 webhook URL")
    logger.info("=" * 60)

    # 启动服务器
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
