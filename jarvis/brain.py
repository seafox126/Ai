"""Core brain module for LLM-backed assistant responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import requests

from .commands import CommandExecutor
from .config import AssistantConfig
from .memory import MemoryStore


class LLMProcessor(Protocol):
    """Contract for LLM-backed response generation."""

    def generate(self, prompt: str) -> str:
        """Return assistant response text for a user prompt."""


class LocalLLM:
    def __init__(self, model: str = "llama3"):
        self.model = model

    def generate(self, prompt: str) -> str:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=30,
        )

        data = response.json()
        return data["response"]


@dataclass
class JarvisBrain:
    """Coordinates memory, commands, and LLM processing."""

    config: AssistantConfig
    memory: MemoryStore
    commands: CommandExecutor
    llm: LLMProcessor

    def handle(self, user_text: str) -> str:
        """Process one user request and return assistant output."""
        stripped = user_text.strip()
        lowered = stripped.lower()

        if lowered.startswith(self.config.command_prefix):
            command_text = stripped[len(self.config.command_prefix) :]
            command_response = self.commands.execute(command_text)
            response = command_response if command_response is not None else "Command not recognized."
        elif lowered.startswith(self.config.remember_prefix):
            note = stripped[len(self.config.remember_prefix) :]
            self.memory.add_note(note)
            response = f"Saved to memory: {note.strip()}"
        elif lowered == self.config.list_memory_command:
            notes = self.memory.list_notes()
            response = "No saved memory yet." if not notes else "Memory: " + "; ".join(notes)
        else:
            response = self.llm.generate(stripped)

        self.memory.add_interaction(user_text=stripped, assistant_text=response)
        return response
