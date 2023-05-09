
from googletrans import Translator#перевод текста
import openai
import config

openai.api_key = config.gpt_key

from translate import Translator


translator= Translator(from_lang = 'ru',to_lang="en")

def translate(text,from_lang):
  if from_lang == 'ru':
    translator = Translator(from_lang = 'ru',to_lang='en')
  elif from_lang == 'en':
    translator = Translator(from_lang='en',to_lang='ru')   

  return translator.translate(text)

def openaiResponse(request,record):
  record.stop()
  request = translate(request,'ru')
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "user", "content":f"{request}"}
    ],
     temperature=0.8
  )
  response = translate(completion.choices[0].message.content,'en')
  return response

  
