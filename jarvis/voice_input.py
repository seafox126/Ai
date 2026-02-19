"""Voice input adapters for microphone speech recognition."""

from __future__ import annotations

from typing import Any, Protocol


class VoiceInput(Protocol):
    """Contract for speech/text input adapters."""

    def listen(self) -> str:
        """Capture and return user utterance as text."""


class SpeechRecognitionVoiceInput:
    """Microphone-based speech-to-text input using `speech_recognition`."""

    def __init__(
        self,
        timeout: int = 5,
        phrase_time_limit: int = 10,
        recognizer: Any | None = None,
        microphone: Any | None = None,
        sr_module: Any | None = None,
    ) -> None:
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit

        self._sr = sr_module
        if self._sr is None:
            try:
                import speech_recognition as sr  # type: ignore
            except ImportError:
                self._sr = None
            else:
                self._sr = sr

        if self._sr is None:
            self.recognizer = None
            self.microphone = None
            return

        self.recognizer = recognizer or self._sr.Recognizer()
        self.microphone = microphone or self._sr.Microphone()

    @property
    def is_available(self) -> bool:
        """Return True when speech recognition dependencies are available."""
        return self._sr is not None and self.recognizer is not None and self.microphone is not None

    def listen(self) -> str:
        """Capture microphone audio and return recognized text.

        Returns an empty string when speech cannot be recognized or audio capture fails.
        """
        if self._sr is None or self.recognizer is None or self.microphone is None:
            return ""

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit,
                )
            text = self.recognizer.recognize_google(audio)
            return text.strip()
        except self._sr.UnknownValueError:
            return ""
        except self._sr.RequestError:
            return ""
        except self._sr.WaitTimeoutError:
            return ""
        except OSError:
            return ""


class ConsoleVoiceInput:
    """Console fallback input adapter for local development."""

    def listen(self) -> str:
        return input("You: ").strip()
