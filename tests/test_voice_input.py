from types import SimpleNamespace

from jarvis.voice_input import SpeechRecognitionVoiceInput


class _UnknownValueError(Exception):
    pass


class _RequestError(Exception):
    pass


class _WaitTimeoutError(Exception):
    pass


class FakeMicrophone:
    def __enter__(self):
        return "source"

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeRecognizer:
    def __init__(self, result: str = "hello world", error: Exception | None = None):
        self.result = result
        self.error = error

    def adjust_for_ambient_noise(self, source, duration=0.3):
        return None

    def listen(self, source, timeout: int, phrase_time_limit: int):
        if self.error:
            raise self.error
        return "audio"

    def recognize_google(self, audio):
        if self.error:
            raise self.error
        return self.result


def _sr_module() -> SimpleNamespace:
    return SimpleNamespace(
        UnknownValueError=_UnknownValueError,
        RequestError=_RequestError,
        WaitTimeoutError=_WaitTimeoutError,
    )


def test_listen_returns_recognized_text() -> None:
    voice = SpeechRecognitionVoiceInput(
        recognizer=FakeRecognizer(result="  turn on lights  "),
        microphone=FakeMicrophone(),
        sr_module=_sr_module(),
    )

    assert voice.listen() == "turn on lights"


def test_listen_returns_empty_on_recognition_error() -> None:
    voice = SpeechRecognitionVoiceInput(
        recognizer=FakeRecognizer(error=_UnknownValueError("cannot parse")),
        microphone=FakeMicrophone(),
        sr_module=_sr_module(),
    )

    assert voice.listen() == ""


def test_listen_returns_empty_on_timeout_error() -> None:
    voice = SpeechRecognitionVoiceInput(
        recognizer=FakeRecognizer(error=_WaitTimeoutError("timeout")),
        microphone=FakeMicrophone(),
        sr_module=_sr_module(),
    )

    assert voice.listen() == ""
