"""Personal mail handler."""

from pathlib import Path
from time import time

from bbs_operator import BBSMessage

MAIL_ROOT = Path("data/mail")


def handle_mail(message: BBSMessage) -> str:
    tokens = message.text.split()
    if len(tokens) < 2:
        return "Mail commands: list, read <n>, send <user> <text>"
    subcommand = tokens[1]
    if subcommand == "list":
        return list_messages(message.sender_id)
    if subcommand == "read" and len(tokens) > 2:
        return read_message(message.sender_id, tokens[2])
    if subcommand == "send" and len(tokens) > 3:
        recipient = tokens[2]
        text = " ".join(tokens[3:])
        return send_message(message.sender_id, recipient, text)
    return "Invalid mail command."


def list_messages(user_id: str) -> str:
    user_dir = MAIL_ROOT / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(user_dir.glob("*.txt"))
    lines = []
    for index, path in enumerate(files, start=1):
        line = f"{index}: {path.name}"
        lines.append(line)
    if not lines:
        return "No messages."
    return "\n".join(lines)


def read_message(user_id: str, index_str: str) -> str:
    user_dir = MAIL_ROOT / user_id
    files = sorted(user_dir.glob("*.txt"))
    try:
        index = int(index_str) - 1
    except ValueError:
        return "Invalid message number."
    if index < 0 or index >= len(files):
        return "Invalid message number."
    path = files[index]
    text = path.read_text(encoding="utf-8")
    path.unlink()
    return text


def send_message(sender_id: str, recipient_id: str, text: str) -> str:
    user_dir = MAIL_ROOT / recipient_id
    user_dir.mkdir(parents=True, exist_ok=True)
    timestamp = str(time())
    path = user_dir / f"{timestamp}.txt"
    body = f"From {sender_id}: {text}"
    path.write_text(body, encoding="utf-8")
    return "Message sent."
