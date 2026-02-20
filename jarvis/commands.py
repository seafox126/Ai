"""Command detection and execution for simple system actions."""

from __future__ import annotations

import platform
import subprocess
from datetime import datetime
from typing import Callable


class CommandExecutor:
    """Detect and execute supported user commands."""

    def __init__(self, runner: Callable[[list[str]], None] | None = None) -> None:
        self.runner = runner or self._default_runner

    def execute(self, command_text: str) -> str | None:
        """Execute a matching command and return a response string.

        Returns None when no command matches.
        """
        text = command_text.strip().lower()

        if text in {"what time is it", "time", "current time"}:
            return f"It is {datetime.now().strftime('%H:%M:%S')}."

        if text in {"open browser", "open the browser"}:
            self._open_browser()
            return "Opening browser."

        if text in {"open notepad", "open notes"}:
            self._open_notepad()
            return "Opening notepad."

        return None

    @staticmethod
    def _default_runner(command: list[str]) -> None:
        subprocess.Popen(command)

    def _open_browser(self) -> None:
        system = platform.system().lower()
        if system == "windows":
            self.runner(["cmd", "/c", "start", "", "https://www.google.com"])
        elif system == "darwin":
            self.runner(["open", "https://www.google.com"])
        else:
            self.runner(["xdg-open", "https://www.google.com"])

    def _open_notepad(self) -> None:
        system = platform.system().lower()
        if system == "windows":
            self.runner(["notepad"])
        elif system == "darwin":
            self.runner(["open", "-a", "TextEdit"])
        else:
            self.runner(["gedit"])
