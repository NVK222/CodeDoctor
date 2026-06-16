from collections.abc import Callable


class Broker:
    def __init__(self) -> None:
        self._subscribers: list[Callable[[str], None]] = []

    def subscribe(self, callback: Callable[[str], None]) -> None:
        self._subscribers.append(callback)

    def notify(self, message: str) -> None:
        for callback in self._subscribers:
            callback(message)
