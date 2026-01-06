"""
Pipecat 语音对话 Bot - SIP 版本
使用 Gemini 2.0 Flash Lite + Deepgram Nova2 + ElevenLabs (印度口音)
通过 Twilio SIP 线路落地
"""

import os
import sys
from loguru import logger
from dotenv import load_dotenv

from pipecat.frames.frames import EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import LLMAssistantResponseAggregator, LLMUserResponseAggregator
from pipecat.services.google import GoogleLLMService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.transports.services.twilio import TwilioTransport
from pipecat.vad.silero import SileroVADAnalyzer

# 加载环境变量
load_dotenv()

# 配置日志
logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


async def main(
    twilio_account_sid: str,
    twilio_auth_token: str,
    twilio_phone_number: str,
    call_sid: str = None
):
    """
    主函数：创建并运行语音对话机器人（SIP版本）

    Args:
        twilio_account_sid: Twilio 账户 SID
        twilio_auth_token: Twilio 认证令牌
        twilio_phone_number: Twilio 电话号码
        call_sid: 通话 SID（可选，用于接听来电）
    """
    # 获取 API 密钥
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

    if not all([gemini_api_key, deepgram_api_key, elevenlabs_api_key]):
        raise ValueError("需要设置所有必需的 API 密钥：GEMINI_API_KEY, DEEPGRAM_API_KEY, ELEVENLABS_API_KEY")

    # 配置 Twilio 传输层（处理 SIP 通话）
    transport = TwilioTransport(
        account_sid=twilio_account_sid,
        auth_token=twilio_auth_token,
        from_phone=twilio_phone_number,
        call_sid=call_sid
    )

    # 配置 Deepgram STT 服务（语音转文本）
    stt = DeepgramSTTService(
        api_key=deepgram_api_key,
        model="nova-2",  # Nova 2 模型
        language="en",   # 英语
    )

    # 配置 Google Gemini LLM 服务
    llm = GoogleLLMService(
        api_key=gemini_api_key,
        model="gemini-2.0-flash-exp",  # Gemini 2.0 Flash Lite
    )

    # 配置 ElevenLabs TTS 服务（文本转语音）
    # 使用印度口音英语，可以选择合适的voice_id
    tts = ElevenLabsTTSService(
        api_key=elevenlabs_api_key,
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam - 可替换为印度口音的 voice_id
        model_id="eleven_multilingual_v2",
        # 可以设置 voice settings 来调整口音
        stability=0.5,
        similarity_boost=0.75,
    )

    # 创建消息聚合器
    user_response = LLMUserResponseAggregator()
    assistant_response = LLMAssistantResponseAggregator()

    # 设置系统提示
    system_prompt = """You are a friendly AI voice assistant speaking with an Indian accent.

Your role:
1. Answer questions concisely and naturally
2. Keep the conversation engaging and warm
3. If unsure, honestly say you don't know
4. Speak in clear, conversational English

Remember: Your responses will be converted to speech, so keep them brief and clear."""

    # 创建处理管道
    pipeline = Pipeline([
        transport.input(),      # 接收音频输入（来自 SIP）
        stt,                    # Deepgram 语音转文字
        user_response,          # 用户消息聚合
        llm,                    # Gemini LLM 处理
        tts,                    # ElevenLabs 文本转语音
        transport.output(),     # 输出音频（到 SIP）
        assistant_response,     # 助手消息聚合
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
    @transport.event_handler("on_call_started")
    async def on_call_started(transport):
        """当通话开始时"""
        logger.info("📞 通话已开始")

        # 发送欢迎消息
        await task.queue_frame(
            assistant_response.create_context_frame([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Please greet the caller warmly in Indian-accented English and introduce yourself briefly."}
            ])
        )

    @transport.event_handler("on_call_ended")
    async def on_call_ended(transport):
        """当通话结束时"""
        logger.info("📞 通话已结束")
        await task.queue_frame(EndFrame())

    # 运行管道
    runner = PipelineRunner()

    logger.info("🤖 SIP 语音助手启动成功！")
    logger.info(f"📞 使用电话号码: {twilio_phone_number}")
    logger.info(f"🧠 模型: Gemini 2.0 Flash Lite")
    logger.info(f"🎤 ASR: Deepgram Nova 2")
    logger.info(f"🔊 TTS: ElevenLabs (印度口音)")

    await runner.run(task)


if __name__ == "__main__":
    import asyncio

    # 从环境变量获取 Twilio 配置
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
        logger.error("❌ 缺少 Twilio 配置，请设置环境变量：")
        logger.error("   - TWILIO_ACCOUNT_SID")
        logger.error("   - TWILIO_AUTH_TOKEN")
        logger.error("   - TWILIO_PHONE_NUMBER")
        sys.exit(1)

    # 从命令行参数获取 call_sid（可选）
    call_sid = sys.argv[1] if len(sys.argv) > 1 else None

    asyncio.run(main(
        twilio_account_sid,
        twilio_auth_token,
        twilio_phone_number,
        call_sid
    ))
