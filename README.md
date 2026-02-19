# Jarvis Modular Assistant (Python)

## Architecture (before code)

This project is organized as a **small core + replaceable adapters** pattern so it stays simple now and scales later.

### Runtime flow
1. `voice_input` captures user speech/text.
2. `brain` decides how to handle the request.
3. `commands` runs local actions when requested.
4. `brain` sends normal conversation to the LLM processor.
5. `memory` stores conversation and user notes.
6. `voice_output` speaks/prints the assistant reply.

### Why this scales
- **Single responsibility per file**: each module owns one concern.
- **Dependency injection in `main.py`**: swap implementations without rewriting logic.
- **Stable interfaces**: easy to plug in Whisper/STT, OpenAI/LLM, and real TTS later.

## Requested folder structure

```text
jarvis/
│
├── main.py
├── brain.py
├── voice_input.py
├── voice_output.py
├── memory.py
├── commands.py
├── config.py
└── memory.json
```

## What each file does

- `jarvis/main.py`: Application entrypoint; wires all modules and runs the assistant loop.
- `jarvis/brain.py`: Core orchestrator for LLM processing, memory updates, and command routing.
- `jarvis/voice_input.py`: Voice/text input abstraction and concrete input adapters.
- `jarvis/voice_output.py`: Text-to-speech abstraction and concrete output adapters.
- `jarvis/memory.py`: JSON-backed memory system for notes and conversation history.
- `jarvis/commands.py`: Command execution module with explicit command handlers.
- `jarvis/config.py`: Central configuration (paths, assistant name, exit keywords).
- `jarvis/memory.json`: Persistent data file for notes/history.

## Run

```bash
python -m jarvis.main
```
