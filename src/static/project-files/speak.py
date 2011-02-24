import threading

import pythoncom
import win32com.client
import win32con
import win32gui

class Voice:
    def __init__(self):
        self._speaker_thread = None
        self._voice = win32com.client.Dispatch('Sapi.SpVoice')

    def _speaker(self, marshalled_voice, text):
        pythoncom.CoInitialize()

        voice = win32com.client.Dispatch(
            pythoncom.CoGetInterfaceAndReleaseStream(
                marshalled_voice,  pythoncom.IID_IDispatch))

        self.pre_speak()

        voice.Speak(text, 3)
        voice.WaitUntilDone(-1)

        self.post_speak()

        pythoncom.CoUninitialize()

    def speak(self, text):
        if not text:
            return None
        if self._speaker_thread and self._speaker_thread.is_alive():
            self.stop()
            self._speaker_thread.join()
        marshalled_voice = pythoncom.CoMarshalInterThreadInterfaceInStream(
             pythoncom.IID_IDispatch, self._voice)
        self._speaker_thread = threading.Thread(
            target=self._speaker, args=(marshalled_voice, text))
        self._speaker_thread.start()

    def stop(self):
        self._voice.Speak('', 3)

    def wait(self):
        if self._speaker_thread and self._speaker_thread.is_alive():
            self._speaker_thread.join()

    def pre_speak(self):
        pass

    def post_speak(self):
        pass


voice = Voice()
voice.speak('Hello, world!')
voice.wait()
