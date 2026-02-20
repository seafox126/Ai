import jarvis.voice_output as voice_output_module


class FakeEngine:
    def __init__(self) -> None:
        self.properties: dict[str, int] = {}
        self.spoken: list[str] = []
        self.ran = 0

    def setProperty(self, name: str, value: int) -> None:
        self.properties[name] = value

    def say(self, text: str) -> None:
        self.spoken.append(text)

    def runAndWait(self) -> None:
        self.ran += 1


def test_speak_uses_engine_and_trims_text() -> None:
    engine = FakeEngine()
    output = voice_output_module.Pyttsx3VoiceOutput(engine=engine)

    output.speak("  hello world  ")

    assert engine.spoken == ["hello world"]
    assert engine.ran == 1


def test_set_rate_updates_engine_rate() -> None:
    engine = FakeEngine()
    output = voice_output_module.Pyttsx3VoiceOutput(rate=170, engine=engine)

    output.set_rate(210)

    assert engine.properties["rate"] == 210
