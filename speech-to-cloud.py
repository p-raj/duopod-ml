import requests
import base64
import json
# from pydub import AudioSegment
from time import sleep

hindi = {
  'tt': 'hi',
  'ts': {
    "languageCode": "hi-IN",
    "name": "hi-IN-Wavenet-C"
  }
}

german = {
  'tt': 'de',
  'ts': {
    "languageCode": "de-DE",
    "name": "de-DE-Wavenet-D"
  }
}

french = {
  'tt': 'fr',
  'ts': {
    "languageCode": "fr-FR",
    "name": "fr-FR-Wavenet-C"
  }
}

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


### dangerous code - used here for scheduling the check
while not done or wait <= 10:
    sleep(10)
    wait += 1
    r2 = requests.get("https://speech.googleapis.com/v1/operations/{}?key={}".format(name, token))
    done = r2.json().get('done', False)
    if done:
        results = r2.json().get('response', None)
        if results:
            results = r2.json().get('response', None).get('results')
    

final = results[0].get('alternatives')[0].get('transcript')

print(final)
# === LONG



lang = hindi

# PART 2 TRANSLATION

url = "https://translation.googleapis.com/language/translate/v2?key={}&q={}&source={}&target={}".format(token, final, "en", lang.get('tt'))

tt = requests.post(url, headers=headers)

try:
    final = tt.json().get('data').get('translations')[0].get('translatedText')
except:
    final = None

# if not final:
#     return None

print (final)
# PART 3 SPEECH TO TEXT

save_long_path = "/Users/praj/Desktop/PIONEER-Hackathon/Naval-{}-Ep65.mp3".format(lang.get('tt'))

payload = {
  "audioConfig": {
    "audioEncoding": "LINEAR16",
    "pitch": 0,
    "speakingRate": 1
  },
  "input": {
    "text": final
  },
  "voice": lang.get('ts')
}

url = "https://texttospeech.googleapis.com/v1beta1/text:synthesize?key={}".format(token)

ts = requests.post(url, data=json.dumps(payload), headers=headers)

audio = ts.json().get('audioContent')

a = audio.encode('UTF-8')
f = open(save_long_path, "wb")
f.write(base64.b64decode(a))
f.close()



