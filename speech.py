from gtts import gTTS
import playsound
import os

def speech(text):
  s = gTTS(text,lang='ru')
  s.save('.mp3')
  playsound.playsound('.mp3')
  os.remove('.mp3')

