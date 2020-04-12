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
    

print (results)

results = [{'alternatives': [{'transcript': "Modern Life on the other hand is more hectic. In other ways the sources of stress that we have or more chronic. Let's define Stress For a Moment physically stress is when something wants to be in two places at one time if I take an iron demon apply pressure to both ends in different directions. I'm creating stress in the beam because of one part wants to be North the apartment 2B South light creates stress on the beam in a person stress is when you can't decide what's important. So then you want two things at once at a mutually incompatible. I want to relax right now, but I need to get some work done. I'm under stress. I need to go to that party, but I also need to go to work. But when you truly give up on something is actually no longer stressful when you accept the sun is completely out of control. There's no point being stressed about it. So it doesn't fly that you have some level of control over it. The mind is constantly creating stress for you through situations where it's being more paranoid or more Angry than is actually warranted for your environment. We want to find peace from my we want to have tools that allow us to not turn off them.", 'confidence': 0.97152513}], 'languageCode': 'en-us'}, {'alternatives': [{'transcript': "But you can't suppress the mind. If I say to you don't think of a white elephant uses out of white elephant. So you can't force the money to anything but with the mind of its own calms down and actually goes away and how do you do that? How do you end up with a more peaceful mind because a more peaceful mind automatically creates a happier person one phrase I like is that piece is happiness at rest happiness is peace in motion a peaceful person doing an activity will end up happy doing that activity, but happy person just sitting there will be peaceful. So the goal actually is not happiness, even though we'll use that term alot. The goal is actually piece. So the question is, how do you get to peace? The first problem getting two piece is that no activity will get you a piece because pieces fundamentally inactivity pieces of sense that everything is fine. And if everything is fine you having physical activity change it so you're physically at peace and you're not making mental activity try and change it either because that'll create mental stress because you want to mentally be somewhere other than you actually are.", 'confidence': 0.97130394}], 'languageCode': 'en-us'}, {'alternatives': [{'transcript': "So piece itself is not a thing that can be directly achieved. You cannot work towards peace. What you can work towards is understanding that think this is an old religious saying what's is the name of God is truth and what that's basically saying is that when you understand certain things when you learn certain things when you're convinced of certain things when they become a deep part of you then you naturally become a more peaceful person.", 'confidence': 0.9521841}], 'languageCode': 'en-us'}]

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



