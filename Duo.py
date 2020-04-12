import boto3
from flask import Flask,request,jsonify
import os
import json
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.cloud import texttospeech
import io
import psycopg2
from multiprocessing import Process
import time
import requests
from google.cloud import translate_v2 as translate
import six
from dotenv import load_dotenv

load_dotenv('/home/veris-bharat/Downloads/duo/.env')

PATH_TO_FILE = os.getenv('PATH_TO_FILE')
UPDATE_STATUS_URL = os.getenv('UPDATE_STATUS_URL')
LANGUAGE_LIST_PATH = os.getenv('LANGUAGE_LIST_PATH')
s3Resource = boto3.resource('s3')


app = Flask(__name__)

def set_failed(mapping_id):
    data = {
        'status': 'Failed'
    }
    r = requests.post(UPDATE_STATUS_URL.format(mapping_id), data=data)
    print(r.status_code, r.text)

def get_recognize(mapping_id, url, language_code, channel_id, episode_id, target_language, title, description):
    try:
        r = requests.get(url)
        local_file_path = "{0}/podcast_{1}_{1}.mp3".format(PATH_TO_FILE, channel_id,episode_id)
        with open(local_file_path, 'wb') as f:
            f.write(r.content)
        f.close()
        client = speech_v1.SpeechClient()
        sample_rate_hertz = 16000

        with open("{0}".format(LANGUAGE_LIST_PATH), 'r') as json_file:
            language_list = json.load(json_file)
        lang = language_list['voice_list'][language_code]

        encoding = enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
        config = {
            "language_code": lang['languageCodes'],
            "sample_rate_hertz": sample_rate_hertz,
            "encoding": encoding
        }
        with io.open(local_file_path, "rb") as f:
            content = f.read()
        f.close()
        audio = {"content": content}

        operation = client.long_running_recognize(config, audio)
        response = operation.result()
        res = []
        for result in response.results:
            alternative = result.alternatives[0]
            res.append(alternative.transcript)

        filename = "{0}/transcript_{1}_{2}.txt".format(PATH_TO_FILE, channel_id,episode_id)
        with open(filename, "w") as file:
            file.write(res[0])
        file.close()

        s3Resource.meta.client.upload_file(filename, 'duopod',
                                           '{0}/{1}/{2}/transcript.txt'.format(channel_id, episode_id, language_code),
                                           ExtraArgs={'ACL': 'public-read'})
        s3_link = "https://duopod.s3.ap-south-1.amazonaws.com/{0}/{1}/{2}/transcript.txt".format(channel_id, episode_id, language_code)

        print("file transcribed")
        data = {
            'status': 'transcribed',
            'transcribed_text_link': s3_link
        }
        r = requests.post(UPDATE_STATUS_URL.format(mapping_id), data=data)
        print(r.status_code, r.text)

    except Exception as e:
        set_failed(mapping_id)
    translate_text(mapping_id, filename, target_language, channel_id, episode_id, title, description)


def translate_text(mapping_id, transcript_file, target_language, channel_id, episode_id, title, description):
    try:
        translate_client = translate.Client()

        with open(transcript_file, 'r') as f:
            text = f.read()
        f.close()

        if isinstance(text, six.binary_type):
            text = text.decode('utf-8')

        result_title = translate_client.translate(title, target_language=target_language)
        translated_title = result_title['translatedText']
        print(translated_title)
        result_description = translate_client.translate(description, target_language=target_language)
        translated_description = result_title['translatedText']

        result = translate_client.translate(text, target_language=target_language)
        translated_text = result['translatedText']
        filename = "{0}/translated_{1}_{2}.txt".format(PATH_TO_FILE, channel_id,episode_id)
        with open(filename, "w") as file:
            file.write(translated_text)
        file.close()

        s3Resource.meta.client.upload_file(filename, 'duopod',
                                           '{0}/{1}/{2}/translated.txt'.format(channel_id, episode_id, target_language),
                                           ExtraArgs={'ACL': 'public-read'})
        s3_link = "https://duopod.s3.ap-south-1.amazonaws.com/{0}/{1}/{2}/translated.txt".format(channel_id, episode_id, target_language)
        print("file translated")
        data = {
            'status' : 'translated',
            'converted_title': translated_title,
            'translated_text_link' : s3_link,
            'description': translated_description
        }
        r = requests.post(UPDATE_STATUS_URL.format(mapping_id), data=data)
        print(r.status_code, r.text)

    except Exception as e:
        set_failed(mapping_id)
    text_to_speech(mapping_id, filename, target_language, channel_id, episode_id)
    

def text_to_speech(mapping_id, text_file, language_code, channel_id, episode_id):
    language_list = {}
    try:
        with open("{0}".format(LANGUAGE_LIST_PATH), 'r') as json_file:
            language_list = json.load(json_file)
        lang = language_list['voice_list'][language_code]
        client = texttospeech.TextToSpeechClient()

        with open(text_file, 'r') as file:
            text = file.read()
        input_text = texttospeech.types.SynthesisInput(text=text)
        if lang['ssmlGender'] == 'MALE':
            ssml_gen = texttospeech.enums.SsmlVoiceGender.MALE
        else:
            ssml_gen = texttospeech.enums.SsmlVoiceGender.FEMALE
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=lang['languageCodes'],
            name=lang['name'],
            ssml_gender=ssml_gen)

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(input_text, voice, audio_config)

        filename = "{0}/podcast_{1}_{2}_{3}.mp3".format(PATH_TO_FILE, language_code, channel_id,episode_id)
        with open(filename, 'wb') as out:
            out.write(response.audio_content)
        out.close()

        s3Resource.meta.client.upload_file(filename, 'duopod',
                                           '{0}/{1}/{2}/podcast.mp3'.format(channel_id, episode_id, language_code),
                                           ExtraArgs={'ACL': 'public-read'})
        s3_link = "https://duopod.s3.ap-south-1.amazonaws.com/{0}/{1}/{2}/podcast.mp3".format(channel_id, episode_id,
                                                                                                  language_code)
        data = {
            'status': 'completed',
            'link': s3_link
        }
        r = requests.post(UPDATE_STATUS_URL.format(mapping_id), data=data)
        print(r.status_code, r.text)

    except Exception as e:
        set_failed(mapping_id)
    print("Process Completed")

@app.route('/dev/start_pipeline',methods=['POST'])
def create_transcript():
    podcast_url = request.json.get('podcast_url')
    podcast_language = request.json.get('podcast_language')
    episode_id = request.json.get('episode_id')
    channel_id = request.json.get('channel_id')
    target_language = request.json.get('target_language')
    title = request.json.get('title')
    mapping_id = request.json.get('language_mapping_id')
    description = request.json.get('description')

    if not podcast_url or not podcast_language or not episode_id or not channel_id or not title:
        return jsonify({"Error": "Incorrect Input", "code": "400"}), 400

    heavy_process = Process(target=get_recognize, daemon=True, args=(mapping_id, podcast_url, podcast_language, channel_id, episode_id, target_language, title, description))
    heavy_process.start()
    
    return jsonify({"message":"your request have been accepted","code":"200"}),200

if __name__=="__main__":
    app.run(debug=True)
