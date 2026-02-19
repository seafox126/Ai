from pathlib import Path

from jarvis.memory import add_to_memory, load_memory, save_memory


def test_load_memory_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    data = load_memory(path)

    assert path.exists()
    assert data["conversation"] == []


def test_add_to_memory_persists_message(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"

    add_to_memory(path, "user", "hello")
    data = load_memory(path)

    assert data["conversation"][-1] == {"role": "user", "message": "hello"}


def test_save_memory_writes_data(tmp_path: Path) -> None:
    path = tmp_path / "memory.json"
    payload = {"conversation": [{"role": "assistant", "message": "ok"}], "notes": []}

    save_memory(path, payload)

    assert load_memory(path)["conversation"][0]["message"] == "ok"
