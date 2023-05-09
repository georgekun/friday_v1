import pvporcupine # для распозавния фразы sunday через токен
import pvrecorder #для потока записи с мкирофона
import playsound#простая библиотека для воспроизведения звука
import random #рандом
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume #для работы со звуком
from fuzzywuzzy import fuzz #для сравнение нечеткого текста. Расстояние ливенштейна
import vosk #нейронка для распознававаниая текста с мкирофона
import struct
 #мои данные из другого файла
import date
import config
from chatGPT import openaiResponse
from speech import speech

#для звука
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL

#дефолтные модули
import time
import json
import os
import webbrowser
import pyautogui

#громкость
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

#иницаиализация поркупине
porcupine = pvporcupine.create(
    access_key=config.porcupine_access,
    keyword_paths=["models/friday/friday.ppn"],
    model_path='models/friday/porcupine_params_ru.pv',
    sensitivities=[0.8]
 )
# работаем с VOSK
model = vosk.Model("models/vosk-model-small-ru-0.4") # поменяе модель на более лучшую. Наверное будет сжираться много оперативки. Изначальная модель на 40мь
#нынешняя модель 1.8гб, не выдерживает нагрузку
samplerate = 16000 # Поменяем на 8000, было 16000, надо посмотреть справляется ли лучше
#хуево работает на 8000, точнее вообще не работает
device = -1
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)



loudness = True #глабально включен звук или нет, чтоб понять возвращать или нет
mode_chatgpt = False # режим чата gpt
record = pvrecorder.PvRecorder(device_index=-1,frame_length=porcupine.frame_length)
volume.SetMute(0,None)
playsound.playsound('sound/run.wav')
print("Запись началась...")
record.start() #первый запуск

#функция для проигрывания музыки
def play(sound):
  record.stop()
  volume.SetMute(0,None)#звуки должны быть слышны
  time.sleep(0.5)
  path = f'sound/{sound}_{random.choice([1,2])}.wav'
  if(sound == 'ok'):
    path = f'sound/{sound}_{random.choice([1,2,3])}.wav'  
  if(sound not in ['greating','ok']):
    path = f'sound/{sound}.wav'
  playsound.playsound(path)
   #а вот вырубать звук или нет надо смотреть по флагу. Если я сказал выруби звук, то флаг становится тру. а значит не надо его обратно включать
  record.start()
  



def cmd(command):
        global loudness,mode_chatgpt
        if(command =="working_mode"):
            os.startfile("C:/Program Files/JetBrains/IntelliJ IDEA Community Edition 2022.3.1/bin/idea64.exe")
            os.startfile("C:/Users/Jordan/AppData/Local/Programs/Microsoft VS Code/Code.exe")
            os.startfile("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe")
            # Получаем список всех процессов
          
        #elif(command =="reboot"):
          # os.system("shutdown -r -t 0")
        elif(command =="music"):
           webbrowser.open_new_tab("https://www.youtube.com/watch?v=NjvaRFnfeFI")
        elif(command =="mute"):
            volume.SetMute(1,None)
            loudness = False #громкость выключена
        elif(command =="unmute"):
            volume.SetMute(0,None)
            loudness = True #громкость включена
        elif(command == "stupid"):
           play("stupid")
        elif(command == "stop"):
           play("thanks")
           time.sleep(0.5)
           os._exit(1)
        elif(command == "ok"):
           play("greating_1")
        elif(command =="thanks"):
           play("thanks")
           
        elif(command in ["right","left","space","close"]):
           if(command == 'space'):
              pyautogui.press("space")
           elif(command == "close"):
              pyautogui.click(1910,10)
           else:
              for i in range(5):
                 pyautogui.press(f"{command}")
        elif(command == "smile"):
            play("smile")
        elif(command == "chatgpt"):
           mode_chatgpt =True
           play("ok")
        else:
          os.startfile(command)

def execute(query):
   value = filter(query)
   if(value == None):
      play("not_found")
   elif(value == "gpt_mode"):
      play('ok')
      otvet =  openaiResponse(query,record)
      speech(otvet) #создаст файл. Запустит плайсоунд. Удалит файл
   else:
      # print("я попал сюда " + value)
      cmd(value)
      if(value not in ["stupid","ok","thanks","smile"]):
            play("ok")
  

       
#напишем функцию, которая будет определять наиболее подходящий ключ
#так скажем фильтер
def filter(query):
   if(fuzz.partial_ratio(query[:7],'Расскажи')>60):
      return "gpt_mode"
   else:
      dict = date.commands.keys()
      max_similarity = 0   #максимальная схожесть. Если задать 0 то и при совпадении символов будет попадаться
      key = date.commands.get(0)
      now = 0
      for keys in dict:
         now = fuzz.partial_ratio(query,keys) #нынешняя схожесть
         # print(f"{keys}  == схожесть {now}")
         if(now>max_similarity):
            max_similarity = now
            key = keys
   #return key #вернем уже конкретный ключ
      print(f"{key} ___ {date.commands.get(key)} ___ {max_similarity}")
      if(max_similarity<60):
         print(now)
         return None
      else:
         return date.commands.get(key)  #либо вернем сразу значения ключа


#полчаем байты, структурируе, отправляем на сервер воск и возваращем текстовую строку
def recognize(byte):
    sp = struct.pack("h" * len(byte), *byte)
    if(kaldi_rec.AcceptWaveform(sp)):
       letter = json.loads(kaldi_rec.Result())["text"]
       if(len(letter)>1):
          print("распознано " + letter)
          return letter
    
#запуск программы
while True:
  

  now = record.read()
  keyword_index = porcupine.process(now) #возвращает -1 если нет активационной фразы
  if keyword_index >= 0:
      play("greating")#приветствие
      volume.SetMute(1,None)#выключаем звук и ждем 10 секунд команды
      print("yes, sir")
      passed_time = 0
      issue_time = time.time()
      count_commands = 0
    
      while passed_time-issue_time<15: #10 секунд еще будет активна активационная фраза passed_time-issue_time<30
         
         passed_time = time.time()
         record.start()
         text = recognize(record.read()) #получаем текст распознаный
         #надо проверить в куда запрос отправлть№
         #если режим chata gpt, то текст уже нужно кидать в функцию чата gpt
         if(text!=None):
             execute(text)

      if(loudness):
            volume.SetMute(0,None)
      else:
            volume.SetMute(1,None)
         
      #если была команад выключить звук, то глабально поменяется флаг, и даже после активации обратно, она будет так как задано командой mute
      
      print("конец.")

  
   
