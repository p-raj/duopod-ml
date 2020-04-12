import requests
import base64
import json
from pydub import AudioSegment
from time import sleep

token = "TOKEN"


# Pass the audio data to an encoding function.
def encode_audio(audio):
  audio_content = audio.read()
  return base64.b64encode(audio_content)


long_path = "/Users/praj/Desktop/PIONEER-Hackathon/Naval-Ep65.mp3"
short_path = "/Users/praj/Desktop/PIONEER-Hackathon/Naval-Ep49.mp3"


long_url = "https://speech.googleapis.com/v1p1beta1/speech:longrunningrecognize?key={}".format(token)
short_url = "https://speech.googleapis.com/v1p1beta1/speech:recognize?key={}".format(token)

f = open(long_path, 'rb')
audio = encode_audio(f)


payload = {
  "audio": {
    "content": audio.decode('UTF-8')
  },
  "config": {
    "enableAutomaticPunctuation": True,
    "encoding": "MP3",
    "sample_rate_hertz": 16000,
    # "encoding": "LINEAR16",
    "languageCode": "en-US",
    "model": "default"
  }
}

headers = {"Content-Type": "application/json; charset=utf-8"}

r = requests.post(long_url, data=json.dumps(payload), headers=headers)

name = r.json().get("name")
results = []

done = False
wait = 0

while not done or wait <= 10:
    sleep(10)
    wait += 1
    r2 = requests.get("https://speech.googleapis.com/v1/operations/{}?key={}".format(name, token))
    done = r2.json().get('done', False)
    if done:
        results = r2.json().get('response', None)
        if results:
            results = r2.json().get('response', None).get('results')
    

print (results)
# === LONG
