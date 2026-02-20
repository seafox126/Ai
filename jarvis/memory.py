"""Memory helpers for loading/saving conversation history in memory.json."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


def load_memory(path: Path) -> dict[str, list[dict[str, str]]]:
    """Load memory from disk, creating an empty structure on first run."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        data = {"conversation": [], "notes": []}
        save_memory(path, data)
        return data

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Backward compatibility with older schema.
    if "conversation" not in data and "history" in data:
        converted: list[dict[str, str]] = []
        for item in data.get("history", []):
            user = item.get("user", "")
            assistant = item.get("assistant", "")
            if user:
                converted.append({"role": "user", "message": user})
            if assistant:
                converted.append({"role": "assistant", "message": assistant})
        data["conversation"] = converted

    data.setdefault("conversation", [])
    data.setdefault("notes", [])
    return data


def save_memory(path: Path, data: dict[str, list[dict[str, str]]]) -> None:
    """Save memory to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def add_to_memory(path: Path, role: str, message: str) -> dict[str, list[dict[str, str]]]:
    """Append one conversation message and persist immediately."""
    text = message.strip()
    if not text:
        return load_memory(path)

    data = load_memory(path)
    data["conversation"].append({"role": role, "message": text})
    save_memory(path, data)
    return data


@dataclass
class MemoryStore:
    """Small wrapper around memory.json for assistant use."""

    path: Path
    _cache: dict[str, list[dict[str, str]]] = field(init=False)

    def __post_init__(self) -> None:
        # Load on startup.
        self._cache = load_memory(self.path)

    def add_note(self, note: str) -> None:
        text = note.strip()
        if not text:
            return
        self._cache["notes"].append({"role": "note", "message": text})
        save_memory(self.path, self._cache)

    def list_notes(self) -> list[str]:
        return [item["message"] for item in self._cache["notes"]]

    def add_interaction(self, user_text: str, assistant_text: str) -> None:
        # Save after each interaction.
        self._cache = add_to_memory(self.path, "user", user_text)
        self._cache = add_to_memory(self.path, "assistant", assistant_text)

    def recent_history(self, limit: int = 5) -> list[dict[str, str]]:
        return self._cache["conversation"][-limit:]
