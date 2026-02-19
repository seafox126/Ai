from jarvis.commands import CommandExecutor


def test_detects_time_command() -> None:
    executor = CommandExecutor(runner=lambda _: None)

    response = executor.execute("what time is it")

    assert response is not None
    assert "It is" in response


def test_open_browser_runs_process() -> None:
    calls: list[list[str]] = []
    executor = CommandExecutor(runner=lambda cmd: calls.append(cmd))

    response = executor.execute("open browser")

    assert response == "Opening browser."
    assert len(calls) == 1


def test_no_match_returns_none() -> None:
    executor = CommandExecutor(runner=lambda _: None)

    assert executor.execute("tell me a joke") is None
