"""
FastAPI 服务器 - 管理语音对话会话
提供 Web 界面和 API 端点
"""

import os
import sys
import asyncio
import subprocess
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import aiohttp
from loguru import logger

# 加载环境变量
load_dotenv()

# 配置日志
logger.remove(0)
logger.add(sys.stderr, level="INFO")

# 创建 FastAPI 应用
app = FastAPI(title="Pipecat 语音助手 Demo")

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


async def create_daily_room() -> dict:
    """创建 Daily.co 房间"""
    daily_api_key = os.getenv("DAILY_API_KEY")

    if not daily_api_key:
        raise ValueError("需要设置 DAILY_API_KEY 环境变量")

    url = "https://api.daily.co/v1/rooms"
    headers = {
        "Authorization": f"Bearer {daily_api_key}",
        "Content-Type": "application/json"
    }

    # 配置房间属性
    data = {
        "properties": {
            "enable_chat": True,
            "enable_emoji_reactions": True,
            "start_video_off": True,
            "start_audio_off": False,
            "enable_screenshare": False,
            "enable_advanced_chat": False,
            "max_participants": 2,
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"创建房间失败: {error_text}")
                raise HTTPException(status_code=500, detail=f"创建房间失败: {error_text}")

            room_info = await response.json()
            logger.info(f"房间创建成功: {room_info['name']}")
            return room_info


async def create_daily_token(room_name: str, is_owner: bool = False) -> str:
    """为房间创建访问令牌"""
    daily_api_key = os.getenv("DAILY_API_KEY")

    url = "https://api.daily.co/v1/meeting-tokens"
    headers = {
        "Authorization": f"Bearer {daily_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "properties": {
            "room_name": room_name,
            "is_owner": is_owner,
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"创建令牌失败: {error_text}")
                raise HTTPException(status_code=500, detail=f"创建令牌失败: {error_text}")

            token_info = await response.json()
            return token_info["token"]


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页 HTML"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>未找到 index.html 文件</h1><p>请确保 index.html 在同一目录</p>",
            status_code=404
        )


@app.post("/api/start-bot")
async def start_bot():
    """
    启动语音助手
    创建 Daily 房间，启动 bot 进程，返回房间信息
    """
    try:
        # 创建房间
        logger.info("正在创建 Daily 房间...")
        room_info = await create_daily_room()

        room_url = room_info["url"]
        room_name = room_info["name"]

        # 为 bot 创建令牌
        logger.info("正在创建 bot 令牌...")
        bot_token = await create_daily_token(room_name, is_owner=True)

        # 为用户创建令牌
        logger.info("正在创建用户令牌...")
        user_token = await create_daily_token(room_name, is_owner=False)

        # 启动 bot 进程
        logger.info(f"正在启动 bot 进程: {room_url}")
        bot_process = subprocess.Popen(
            [sys.executable, "bot.py", room_url, bot_token],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # 存储进程信息
        bot_processes[room_name] = {
            "process": bot_process,
            "room_url": room_url,
            "started_at": datetime.now().isoformat()
        }

        logger.info(f"✅ Bot 启动成功！房间: {room_name}")

        return JSONResponse({
            "room_url": room_url,
            "room_name": room_name,
            "token": user_token,
            "bot_started": True,
            "message": "语音助手已启动，正在准备中..."
        })

    except Exception as e:
        logger.error(f"启动 bot 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")


@app.post("/api/stop-bot/{room_name}")
async def stop_bot(room_name: str):
    """停止指定房间的 bot"""
    if room_name not in bot_processes:
        raise HTTPException(status_code=404, detail="未找到该房间的 bot")

    try:
        bot_info = bot_processes[room_name]
        process = bot_info["process"]

        # 终止进程
        process.terminate()
        process.wait(timeout=5)

        # 删除记录
        del bot_processes[room_name]

        logger.info(f"Bot 已停止: {room_name}")

        return JSONResponse({
            "success": True,
            "message": f"Bot 已停止: {room_name}"
        })

    except Exception as e:
        logger.error(f"停止 bot 失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"停止失败: {str(e)}")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return JSONResponse({
        "status": "healthy",
        "active_bots": len(bot_processes),
        "timestamp": datetime.now().isoformat()
    })


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理所有 bot 进程"""
    logger.info("正在关闭服务器，清理资源...")

    for room_name, bot_info in bot_processes.items():
        try:
            process = bot_info["process"]
            process.terminate()
            process.wait(timeout=5)
            logger.info(f"已停止 bot: {room_name}")
        except Exception as e:
            logger.error(f"清理 bot 失败 {room_name}: {e}")


if __name__ == "__main__":
    import uvicorn

    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 7860))

    logger.info(f"🚀 启动服务器: http://{host}:{port}")

    # 启动服务器
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
