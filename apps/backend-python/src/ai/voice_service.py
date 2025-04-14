import os
import time
import pygame
import edge_tts
import asyncio

def play_text_to_speech(text, language='en', slow=False):
    temp_audio_file = "temp_audio.mp3"
    
    async def _main():
        communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
        await communicate.save(temp_audio_file)
    
    asyncio.run(_main())

    pygame.mixer.init()
    pygame.mixer.music.load(temp_audio_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()

    time.sleep(3)
    os.remove(temp_audio_file)
