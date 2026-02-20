from pathlib import Path
from types import SimpleNamespace

import jarvis.brain as brain_module
import jarvis.commands as commands_module
import jarvis.config as config_module
import jarvis.memory as memory_module


class EchoLLM:
    def generate(self, prompt: str) -> str:
        return f"echo:{prompt}"


class FakeResponse:
    def json(self) -> dict[str, str]:
        return {"response": "concise answer"}


def _build(tmp_path: Path) -> brain_module.JarvisBrain:
    config = config_module.AssistantConfig(memory_file=tmp_path / "memory.json")
    return brain_module.JarvisBrain(
        config=config,
        memory=memory_module.MemoryStore(path=config.memory_file),
        commands=commands_module.CommandExecutor(),
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


def test_local_llm_calls_ollama(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_post(url: str, json: dict, timeout: int):
        calls.append({"url": url, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr(brain_module.requests, "post", fake_post)
    llm = brain_module.LocalLLM(model="llama3")

    result = llm.generate("hello")

    assert result == "concise answer"
    assert calls[0]["url"] == "http://localhost:11434/api/generate"
    assert calls[0]["json"]["prompt"] == "hello"
