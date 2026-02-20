"""Voice output using pyttsx3 text-to-speech."""

from __future__ import annotations

from typing import Any, Protocol


class VoiceOutput(Protocol):
    """Contract for output adapters."""

    def speak(self, text: str) -> None:
        """Speak text to the user."""


class Pyttsx3VoiceOutput:
    """pyttsx3-backed text-to-speech output with speed control."""

    def __init__(self, rate: int = 180, engine: Any | None = None) -> None:
        if engine is not None:
            self.engine = engine
        else:
            try:
                import pyttsx3  # type: ignore
            except ImportError as exc:
                raise RuntimeError("pyttsx3 is required. Install with: pip install pyttsx3") from exc
            self.engine = pyttsx3.init()

        self.rate = rate
        self.engine.setProperty("rate", self.rate)

    def set_rate(self, rate: int) -> None:
        """Update speaking speed (words per minute approximation)."""
        self.rate = rate
        self.engine.setProperty("rate", self.rate)

    def speak(self, text: str) -> None:
        """Convert text to speech."""
        cleaned = text.strip()
        if not cleaned:
            return
        self.engine.say(cleaned)
        self.engine.runAndWait()


_default_speaker: Pyttsx3VoiceOutput | None = None


def speak(text: str, rate: int | None = None) -> None:
    """Simple function interface: speak text with optional speed control."""
    global _default_speaker
    if _default_speaker is None:
        _default_speaker = Pyttsx3VoiceOutput(rate=rate or 180)
    elif rate is not None:
        _default_speaker.set_rate(rate)

    _default_speaker.speak(text)
