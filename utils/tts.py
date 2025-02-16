import io
import asyncio
from typing import Any, Coroutine
import pygame
from edge_tts import Communicate

class SimpleTTS:
    def __init__(self, voice: str = "zh-CN-YunxiNeural", rate: str = "+0%", volume: str = "+0%"):
        self.voice = voice
        self.rate = rate
        self.volume = volume

    @property
    def voice(self):
        return self._voice
    
    @voice.setter
    def voice(self, value: str):
        self._voice = value

    @property
    def rate(self):
        return self._rate
    
    @rate.setter
    def rate(self, value: str):
        self._rate = value

    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self, value: str):
        self._volume = value

    async def _load(self, text: str) -> tuple[bool, io.BytesIO | None]:
        try:
            # 创建 Communicate 对象
            communicate = Communicate(text, voice=self.voice, rate=self.rate, volume=self.volume)

            # 获取音频数据流
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]

            # 使用 pygame 播放音频
            return True, io.BytesIO(audio_data)
        except Exception as e:
            print(f"Error: {type(e)} - {e}")

        return False, None

    async def _say(self, text: str, output: str | None = None) -> bool:
        ret, buf = await self._load(text)
        if not ret or buf is None:
            return False

        if output is not None:
            bytes = buf.read()
            with open(output, "wb") as f:
                f.write(bytes)

            buf.seek(0)
                    
        sound = pygame.mixer.Sound(buf)
        sound.play()
        pygame.time.wait(int(sound.get_length() * 1000))  # get_length() 返回音频长度（秒）
        return True

    def load(self, text: str) -> tuple[bool, io.BytesIO | None]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self._load(text))
        loop.close()

        return result
    
    async def asyncLoad(self, text: str) -> Coroutine[Any, Any, tuple[bool, io.BytesIO | None]]:
        return self._load(text)

    def say(self, text: str, output: str | None = None) -> bool:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self._say(text, output))
        loop.close()

        return result

    async def asyncSay(self, text: str, output: str | None = None) -> Coroutine[Any, Any, bool]:
        return self._say(text, output)
    
if __name__ == "__main__":
    pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=2048)  # 设置采样率、位深度和声道数
    pygame.init()

    tts = SimpleTTS()
    tts.say("你好，世界")
    tts.say("徐晨皓你是最棒的", "edge-tts-demo.mp3")
    # tts.asyncSay("你好，世界")