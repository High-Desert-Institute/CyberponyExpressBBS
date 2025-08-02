"""Public bulletin board handler."""

from pathlib import Path
from time import time

from bbs_operator import BBSMessage

BOARD_ROOT = Path("data/board")


def handle_board(message: BBSMessage) -> str:
    tokens = message.text.split()
    if len(tokens) < 2:
        return "Board commands: post <thread> <text>, read <thread>"
    subcommand = tokens[1]
    if subcommand == "read" and len(tokens) > 2:
        return read_thread(tokens[2])
    if subcommand == "post" and len(tokens) > 3:
        thread = tokens[2]
        text = " ".join(tokens[3:])
        return post_thread(message.sender_id, thread, text)
    return "Invalid board command."


def read_thread(thread: str) -> str:
    thread_dir = BOARD_ROOT / thread
    files = sorted(thread_dir.glob("*.txt"))
    lines = []
    for path in files:
        entry = path.read_text(encoding="utf-8")
        lines.append(entry)
    if not lines:
        return "No posts."
    return "\n".join(lines)


def post_thread(sender_id: str, thread: str, text: str) -> str:
    thread_dir = BOARD_ROOT / thread
    thread_dir.mkdir(parents=True, exist_ok=True)
    timestamp = str(time())
    path = thread_dir / f"{timestamp}.txt"
    body = f"{sender_id}: {text}"
    path.write_text(body, encoding="utf-8")
    return "Post added."
