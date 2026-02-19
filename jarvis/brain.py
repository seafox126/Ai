"""Core brain module that connects Jarvis to OpenAI."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol

from jarvis.commands import CommandExecutor
from jarvis.config import AssistantConfig
from jarvis.memory import MemoryStore


class LLMProcessor(Protocol):
    """Contract for LLM-backed response generation."""

    def generate(self, prompt: str) -> str:
        """Return assistant response text for a user prompt."""


class OpenAILLM:
    """OpenAI chat client with short-term conversation memory."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        system_prompt: str = "You are concise, clear, and helpful.",
        max_turns: int = 6,
        api_key: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.max_turns = max_turns
        if client is not None:
            self.client = client
        else:
            try:
                from openai import OpenAI  # type: ignore
            except ImportError as exc:
                raise RuntimeError("openai package is required. Install with: pip install openai") from exc
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    def generate(self, prompt: str) -> str:
        """Send user input to OpenAI and return a clean response."""
        text = prompt.strip()
        self._messages.append({"role": "user", "content": text})
        self._trim_short_term_memory()

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self._messages,
            temperature=0.2,
        )
        raw = completion.choices[0].message.content or ""
        response = self._clean_response(raw)

        self._messages.append({"role": "assistant", "content": response})
        self._trim_short_term_memory()
        return response

    @staticmethod
    def _clean_response(text: str) -> str:
        """Normalize whitespace for cleaner assistant output."""
        return "\n".join(line.strip() for line in text.strip().splitlines() if line.strip())

    def _trim_short_term_memory(self) -> None:
        """Keep system message + latest N user/assistant turns."""
        if len(self._messages) <= 1:
            return

        max_messages = 1 + (self.max_turns * 2)
        self._messages = [self._messages[0], *self._messages[-(max_messages - 1) :]]


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
