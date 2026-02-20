"""Main runtime loop for Jarvis assistant."""

from __future__ import annotations

from brain import JarvisBrain, OpenAILLM
from jarvis.commands import CommandExecutor
from jarvis.config import AssistantConfig
from jarvis.memory import MemoryStore
from jarvis.voice_input import ConsoleVoiceInput, SpeechRecognitionVoiceInput, VoiceInput
from jarvis.voice_output import Pyttsx3VoiceOutput, VoiceOutput


class ConsoleVoiceOutput:
    """Simple console fallback when pyttsx3 is unavailable."""

    def speak(self, text: str) -> None:
        print(f"Assistant: {text}")


def build_assistant() -> tuple[JarvisBrain, MemoryStore, CommandExecutor, VoiceInput, VoiceOutput]:
    """Initialize memory and wire all modules."""
    config = AssistantConfig()
    memory = MemoryStore(path=config.memory_file)
    commands = CommandExecutor()
    brain = JarvisBrain(
        config=config,
        memory=memory,
        commands=commands,
        llm=OpenAILLM(system_prompt=config.system_prompt),
    )

    speech_listener = SpeechRecognitionVoiceInput()
    listener: VoiceInput = speech_listener if speech_listener.is_available else ConsoleVoiceInput()

    try:
        speaker: VoiceOutput = Pyttsx3VoiceOutput()
    except RuntimeError:
        speaker = ConsoleVoiceOutput()

    return brain, memory, commands, listener, speaker


def run() -> None:
    """Run continuously until user says 'shutdown'."""
    brain, memory, commands, listener, speaker = build_assistant()
    speaker.speak("Jarvis is online. Say 'shutdown' to stop.")

    while True:
        user_text = listener.listen().strip()
        if not user_text:
            continue

        if user_text.lower() == "shutdown":
            speaker.speak("Shutting down.")
            break

        command_response = commands.execute(user_text)
        if command_response is not None:
            response = command_response
            memory.add_interaction(user_text=user_text, assistant_text=response)
        else:
            response = brain.handle(user_text)

        speaker.speak(response)


def main() -> None:
    run()


if __name__ == "__main__":
    main()
