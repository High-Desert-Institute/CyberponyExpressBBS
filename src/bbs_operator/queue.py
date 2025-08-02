"""Queue implementations for BBS messages."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from .message import BBSMessage


class MessageQueue:
    """Abstract message queue."""

    def push(self, message: BBSMessage) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def pop(self) -> BBSMessage | None:  # pragma: no cover - interface
        raise NotImplementedError

    def ack(self, message: BBSMessage) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class FileMessageQueue(MessageQueue):
    """Stores messages as JSON files."""

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def push(self, message: BBSMessage) -> None:
        path = self._path_for(message)
        data = asdict(message)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle)

    def pop(self) -> BBSMessage | None:
        files = sorted(self.directory.glob("*.json"))
        if not files:
            return None
        path = files[0]
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        data["context"] = {"path": str(path)}
        message = BBSMessage(**data)
        return message

    def ack(self, message: BBSMessage) -> None:
        path_str = None
        if message.context is not None:
            path_str = message.context.get("path")
        if path_str is None:
            return
        path = Path(path_str)
        if path.exists():
            path.unlink()

    def _path_for(self, message: BBSMessage) -> Path:
        name = f"{message.timestamp}-{message.sender_id}.json"
        path = self.directory / name
        return path
