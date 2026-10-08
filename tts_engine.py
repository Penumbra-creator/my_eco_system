import win32com.client

class HybridTTS:
    def __init__(self):
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        self.speaker.Rate = 0   # скорость (от -10 до 10)
        self.speaker.Volume = 100

    def speak(self, text):
        if text:
            self.speaker.Speak(text)