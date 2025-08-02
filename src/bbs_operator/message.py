"""Message structures for the BBS operator."""

from dataclasses import dataclass


@dataclass
class BBSMessage:
    """Represents a message received from the mesh."""

    sender_id: str
    text: str
    timestamp: float
    context: dict | None = None
