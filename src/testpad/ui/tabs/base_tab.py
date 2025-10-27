from __future__ import annotations
from typing import Any, Dict, Protocol
from PySide6.QtWidgets import QWidget

class ITab(Protocol):
    def save_state(self) -> Dict[str, Any]: ...
    def restore_state(self, state: Dict[str, Any]) -> None: ...
    def on_show(self) -> None: ...
    def on_close(self) -> None: ...

class BaseTab(QWidget):
    def save_state(self) -> Dict[str, Any]:
        return {}

    def restore_state(self, state: Dict[str, Any]) -> None:
        pass

    def on_show(self) -> None:
        pass

    def on_close(self) -> None:
        pass