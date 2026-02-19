from jarvis.main import run


class FakeListener:
    def __init__(self, items: list[str]) -> None:
        self.items = items

    def listen(self) -> str:
        return self.items.pop(0)


class FakeSpeaker:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def speak(self, text: str) -> None:
        self.messages.append(text)


class FakeMemory:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def add_interaction(self, user_text: str, assistant_text: str) -> None:
        self.calls.append((user_text, assistant_text))


class FakeCommands:
    def execute(self, text: str):
        if text == "open browser":
            return "Opening browser."
        return None


class FakeBrain:
    def handle(self, text: str) -> str:
        return f"brain:{text}"


def test_run_routes_command_then_brain_and_shutdown(monkeypatch) -> None:
    listener = FakeListener(["open browser", "hello", "shutdown"])
    speaker = FakeSpeaker()
    memory = FakeMemory()

    def _build():
        return FakeBrain(), memory, FakeCommands(), listener, speaker

    monkeypatch.setattr("jarvis.main.build_assistant", _build)

    run()

    assert speaker.messages[0] == "Jarvis is online. Say 'shutdown' to stop."
    assert "Opening browser." in speaker.messages
    assert "brain:hello" in speaker.messages
    assert speaker.messages[-1] == "Shutting down."
    assert memory.calls == [("open browser", "Opening browser.")]
