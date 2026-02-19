from pathlib import Path
from types import SimpleNamespace

from jarvis.brain import JarvisBrain, OpenAILLM
from jarvis.commands import CommandExecutor
from jarvis.config import AssistantConfig
from jarvis.memory import MemoryStore


class EchoLLM:
    def generate(self, prompt: str) -> str:
        return f"echo:{prompt}"


class FakeCompletions:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="  concise answer  \n\n"))]
        )


def _build(tmp_path: Path) -> JarvisBrain:
    config = AssistantConfig(memory_file=tmp_path / "memory.json")
    return JarvisBrain(
        config=config,
        memory=MemoryStore(path=config.memory_file),
        commands=CommandExecutor(),
        llm=EchoLLM(),
    )


def test_remember_and_show_memory(tmp_path: Path) -> None:
    brain = _build(tmp_path)

    brain.handle("remember buy eggs")
    response = brain.handle("show memory")

    assert "buy eggs" in response


def test_command_execution(tmp_path: Path) -> None:
    brain = _build(tmp_path)

    response = brain.handle("run what time is it")

    assert "It is" in response


def test_default_llm_path(tmp_path: Path) -> None:
    brain = _build(tmp_path)

    response = brain.handle("hello")

    assert response == "echo:hello"


def test_openai_llm_cleans_and_keeps_short_memory() -> None:
    fake_completions = FakeCompletions()
    fake_client = SimpleNamespace(chat=SimpleNamespace(completions=fake_completions))
    llm = OpenAILLM(client=fake_client, max_turns=2)

    llm.generate("one")
    llm.generate("two")
    llm.generate("three")

    assert len(fake_completions.calls) == 3
    assert llm.generate("four") == "concise answer"
