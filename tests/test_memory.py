from pathlib import Path

import jarvis.memory as memory_module


def test_load_memory_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    data = memory_module.load_memory(path)

    assert path.exists()
    assert data["conversation"] == []


def test_add_to_memory_persists_message(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"

    memory_module.add_to_memory(path, "user", "hello")
    data = memory_module.load_memory(path)

    assert data["conversation"][-1] == {"role": "user", "message": "hello"}


def test_save_memory_writes_data(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    payload = {"conversation": [{"role": "assistant", "message": "ok"}], "notes": []}

    memory_module.save_memory(path, payload)

    assert memory_module.load_memory(path)["conversation"][0]["message"] == "ok"
