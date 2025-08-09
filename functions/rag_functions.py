import whisper
import pyttsx3

def speech_to_text(speech_file: str):
    model = whisper.load_model("base")
    result = model.transcribe(speech_file)
    print (result["text"])

def text_to_speech(text: str):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.thomas')
    engine.save_to_file(text, r"C:\Users\tallar\Documents\PROJETS\GenAI\docs\mp3\audio.mp3")
    engine.say(text)
    engine.runAndWait()

text_to_speech("Bonjour ! Ceci est un test de synthèse vocale générée par une intelligence artificielle.")
speech_to_text(r"C:\Users\tallar\Documents\PROJETS\GenAI\docs\mp3\audio.mp3")

