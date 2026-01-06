"""
Pipecat 语音对话 Bot
这是一个简单的语音助手，可以通过语音与用户对话
"""

import os
import sys
from loguru import logger
from dotenv import load_dotenv

from pipecat.frames.frames import EndFrame, LLMMessagesFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.vad.silero import SileroVADAnalyzer

# 加载环境变量
load_dotenv()

# 配置日志
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


async def main(room_url: str, token: str = None):
    """
    主函数：创建并运行语音对话机器人

    Args:
        room_url: Daily.co 房间 URL
        token: Daily.co 访问令牌（可选）
    """
    # 获取 API 密钥
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise ValueError("需要设置 OPENAI_API_KEY 环境变量")

    # 配置 Daily 传输层（处理实时音视频）
    transport = DailyTransport(
        room_url,
        token,
        "语音助手",
        DailyParams(
            audio_out_enabled=True,
            audio_out_sample_rate=16000,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            transcription_enabled=True,
        )
    )

    # 配置 OpenAI LLM 服务
    llm = OpenAILLMService(
        api_key=openai_api_key,
        model="gpt-4"
    )

    # 设置对话上下文和系统提示
    context = OpenAILLMContext(
        messages=[
            {
                "role": "system",
                "content": """你是一个友好的语音助手。你的任务是：
                1. 用简短、自然的语言回答问题
                2. 保持对话轻松愉快
                3. 如果不确定，诚实地说你不知道
                4. 用中文回答（除非用户用其他语言）

                请记住：你的回答会被转成语音，所以要简洁明了。"""
            }
        ]
    )

    # 配置文本转语音（使用 OpenAI TTS）
    tts = transport.tts_service()

    # 创建处理管道
    pipeline = Pipeline([
        transport.input(),   # 接收音频输入
        llm,                 # LLM 处理
        tts,                 # 文本转语音
        transport.output(),  # 输出音频
    ])

    # 创建任务
    task = PipelineTask(
        pipeline,
        PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
        )
    )

    # 注册事件处理器
    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        """当第一个用户加入时，发送欢迎消息"""
        logger.info(f"参与者加入: {participant['id']}")

        # 发送初始问候
        await task.queue_frames([
            LLMMessagesFrame([
                {
                    "role": "system",
                    "content": "请用友好的方式问候用户，并简短介绍你自己。"
                }
            ])
        ])

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        """当用户离开时，结束会话"""
        logger.info(f"参与者离开: {participant['id']}")
        await task.queue_frame(EndFrame())

    @transport.event_handler("on_dialin_ready")
    async def on_dialin_ready(transport, cdata):
        """拨入准备就绪"""
        logger.info(f"拨入准备就绪: {cdata}")

    @transport.event_handler("on_call_state_updated")
    async def on_call_state_updated(transport, state):
        """通话状态更新"""
        logger.info(f"通话状态: {state}")

    # 设置上下文
    task.set_context(context)

    # 运行管道
    runner = PipelineRunner()

    logger.info("🤖 语音助手启动成功！")
    logger.info(f"📞 房间 URL: {room_url}")

    await runner.run(task)


if __name__ == "__main__":
    import asyncio

    # 从命令行参数获取房间 URL 和令牌
    if len(sys.argv) < 2:
        print("用法: python bot.py <room_url> [token]")
        sys.exit(1)

    room_url = sys.argv[1]
    token = sys.argv[2] if len(sys.argv) > 2 else None

    asyncio.run(main(room_url, token))
