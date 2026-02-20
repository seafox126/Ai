"""Configuration for the Jarvis assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AssistantConfig:
    """Central runtime settings."""

    name: str = "Jarvis"
    memory_file: Path = Path("jarvis/memory.json")
    exit_keywords: tuple[str, ...] = ("exit", "quit", "stop")
    command_prefix: str = "run "
    remember_prefix: str = "remember "
    list_memory_command: str = "show memory"
    system_prompt: str = (
        "You are a concise and helpful personal AI assistant. "
        "Keep responses practical."
    )
