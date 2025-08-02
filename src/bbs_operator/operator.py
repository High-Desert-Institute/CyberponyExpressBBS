"""Meshtastic operator that bridges the radio and the queue."""

from time import time
from pubsub import pub
from meshtastic.serial_interface import SerialInterface

from .message import BBSMessage
from .queue import MessageQueue


class BBSOperator:
    """Connects to the Meshtastic device and queues incoming messages."""

    def __init__(self, dev_path: str, queue: MessageQueue):
        self.dev_path = dev_path
        self.queue = queue
        self.interface: SerialInterface | None = None

    def connect(self) -> None:
        self.interface = SerialInterface(devPath=self.dev_path)
        pub.subscribe(self.on_receive, "meshtastic.receive.text")

    def close(self) -> None:
        if self.interface is None:
            return
        self.interface.close()
        self.interface = None

    def on_receive(self, packet: dict, iface: SerialInterface) -> None:
        sender = str(packet.get("from", ""))
        data = packet.get("decoded", {})
        text = data.get("text", "")
        now = time()
        message = BBSMessage(sender_id=sender, text=text, timestamp=now)
        self.queue.push(message)

    def send_text(self, destination: str, text: str) -> dict:
        if self.interface is None:
            raise RuntimeError("Interface not connected")
        packet = self.interface.sendText(text, destinationId=destination)
        return packet
