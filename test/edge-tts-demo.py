import io
import asyncio
import pygame
from edge_tts import Communicate

async def stream_and_play_with_pygame():
    # 初始化 pygame
    pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=2048)  # 设置采样率、位深度和声道数
    pygame.init()

    # 创建 Communicate 对象
    communicate = Communicate(text="大家好，我是徐晨皓。我是徐枫和高明珠的孩子，我特别喜欢做动画。", voice="zh-CN-YunxiNeural")

    # 获取音频数据流
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    # 使用 pygame 播放音频
    sound = pygame.mixer.Sound(io.BytesIO(audio_data))
    sound.play()

    # 等待音频播放完成
    pygame.time.wait(int(sound.get_length() * 1000))  # get_length() 返回音频长度（秒）

    # 退出 pygame
    pygame.quit()

# 运行异步任务
asyncio.run(stream_and_play_with_pygame())