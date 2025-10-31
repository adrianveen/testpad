from __future__ import annotations

from typing import Any, Protocol

from PySide6.QtWidgets import QWidget


class ITab(Protocol):
    def save_state(self) -> dict[str, Any]: ...
    def restore_state(self, state: dict[str, Any]) -> None: ...
    def on_show(self) -> None: ...
    def on_close(self) -> None: ...

class BaseTab(QWidget):
    def save_state(self) -> dict[str, Any]:
        return {}

    def restore_state(self, state: dict[str, Any]) -> None:
        pass

    def on_show(self) -> None:
        pass

    def on_close(self) -> None:
        pass
