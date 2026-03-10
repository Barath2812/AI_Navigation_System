import threading
import pyttsx3
import config

class VoiceSystem:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', config.VOICE_RATE)
        self.is_speaking = False
        self.lock = threading.Lock()

    def speak(self, text):
        """
        Speak text in a non-blocking thread to avoid freezing video feed.
        Skips if already speaking.
        """
        if text and not self.is_speaking:
            thread = threading.Thread(target=self._speak_thread, args=(text,))
            thread.daemon = True
            thread.start()

    def _speak_thread(self, text):
        with self.lock:
            self.is_speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_speaking = False
