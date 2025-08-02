"""Service host that dispatches messages to handlers."""

from time import sleep
from typing import Callable

from bbs_operator import BBSOperator, MessageQueue, BBSMessage


class ServiceHost:
    """Polls the queue and routes messages to handlers."""

    def __init__(self, operator: BBSOperator, queue: MessageQueue):
        self.operator = operator
        self.queue = queue
        self.handlers: dict[str, Callable[[BBSMessage], str]] = {}

    def register_handler(self, command: str, handler: Callable[[BBSMessage], str]) -> None:
        self.handlers[command] = handler

    def run(self) -> None:
        while True:
            message = self.queue.pop()
            if message is None:
                sleep(0.1)
                continue
            parts = message.text.split()
            if not parts:
                reply = "Empty command."
            else:
                command = parts[0]
                handler = self.handlers.get(command)
                if handler is None:
                    reply = "Unknown command."
                else:
                    reply = handler(message)
            self.operator.send_text(message.sender_id, reply)
            self.queue.ack(message)
