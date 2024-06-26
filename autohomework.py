import pyaudio
import wave
import speech_recognition as sr
from pynput.keyboard import Key, Controller
import requests
import time

# 百度翻译API信息
api_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
app_id = "20231213001909570"
api_key = "xBZvpPMAufwuu4vAEXPb"

# 初始化键盘控制器
keyboard = Controller()

# 录音参数
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100
record_seconds = 3

# 初始化语音识别器
recognizer = sr.Recognizer()

# 初始化Pyaudio
p = pyaudio.PyAudio()

# 录音函数
def record_audio(wave_output_filename):
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("* 开始录音")
    frames = []

    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("* 录音结束")

    stream.stop_stream()
    stream.close()

    wf = wave.open(wave_output_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# 语音转文字函数
def speech_to_text(audio_filename):
    with sr.AudioFile(audio_filename) as source:
        try:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            print("未能识别语音，请重试。")

# 文字翻译函数
def translate_text(text, src_lang, dest_lang):
    params = {
        'q': text,
        'from': src_lang,
        'to': dest_lang,
        'appid': app_id,
        'salt': str(time.time()),
        'sign': create_sign(text, app_id, api_key)
    }
    response = requests.get(api_url, params=params)
    result = response.json()
    return result['trans_result'][0]['dst']

# 创建翻译签名
def create_sign(q, appid, key):
    import hashlib
    salt = str(time.time())
    sign = hashlib.md5((appid + q + salt + key).encode('utf-8')).hexdigest()
    return sign

# 模拟键盘输入函数
def simulate_typing(input_text):
    keyboard.type(input_text)
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)

# 主循环
print('将在5秒后开始运行....')
time.sleep(5)
print('开始运行！')
print('【输入】按下Enter播放音频')
keyboard.press(Key.enter)
keyboard.release(Key.enter)
print ("-------------------------")
while True:
    while True:
        audio_filename = "temp_audio.wav"
        record_audio(audio_filename)
        text = speech_to_text(audio_filename)
        print ('【转文字】语音=>'+str(text))
        simulate_typing(text)
        translated_text = translate_text(text, 'en', 'zh')
        print ("【翻译】"+str(text)+"=>"+str(translated_text))
        print ("【输入】模拟输入中")
        simulate_typing(translated_text)
        print ("【完成】下一个单词")
        print ("-------------------------")
