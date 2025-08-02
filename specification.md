# Cyberpony Express BBS Specification

This document describes how the Cyberpony Express BBS package will be built to satisfy the roadmap.  It outlines module relationships, core function definitions and extension points.

## Architectural overview

```
Meshtastic Radio ──USB── BBS Operator ──Queue── Service Host ──Plugins
```

* **Meshtastic Radio** – A T‑Beam or similar device running official Meshtastic firmware.
* **BBS Operator** – Python module that communicates with the radio, parses packets and queues requests.
* **Service Host** – Python framework that processes queued requests, runs services and sends replies.
* **Plugins** – Modular services (mail, librarian, MUD, games) loaded by the service host.

Both main packages live under `src/` and are designed for low power devices.  Operator and host interact through a simple queue that can be backed by files, memory or another store.

## Phase 1 – Core BBS

### Goals

* Implement the `bbs_operator` package.
* Implement the `service_host` framework.
* Provide basic mail and bulletin board features.

### bbs_operator package

```
src/bbs_operator/
    __init__.py
    operator.py
    message.py
    queue.py
```

#### operator.BBSOperator

Connects to the Meshtastic device and routes packets into the message queue.

* `BBSOperator(dev_path: str)` – constructor stores the serial device path.
* `connect() -> None`
    * Calls `meshtastic.serial_interface.SerialInterface` with `devPath`.
    * Subscribes to `meshtastic.receive.text` via `pubsub.pub`.
* `close() -> None` – closes the `SerialInterface`.
* `on_receive(packet: dict, iface: SerialInterface) -> None`
    * Extracts sender and text from the Meshtastic packet.
    * Builds a `BBSMessage` object and pushes it to the queue.
* `send_text(destination: str, text: str) -> dict`
    * Wrapper around `SerialInterface.sendText` for use by the service host.

#### message.BBSMessage

Small dataclass representing incoming requests.

* `sender_id: str`
* `text: str`
* `timestamp: float`
* `context: dict | None`

#### queue.MessageQueue

Abstract queue with a file‑based default implementation.

* `push(message: BBSMessage) -> None`
* `pop() -> BBSMessage | None`
* `ack(message: BBSMessage) -> None`

The operator uses `push`, while the service host uses `pop` and `ack`.

### service_host package

```
src/service_host/
    __init__.py
    host.py
    handlers/
        __init__.py
        mail.py
        board.py
```

#### host.ServiceHost

Runs on the Raspberry Pi, polls the queue and dispatches messages to registered handlers.

* `ServiceHost(operator: BBSOperator, queue: MessageQueue)`
* `register_handler(command: str, handler: Callable[[BBSMessage], str]) -> None`
* `run() -> None`
    * Loop: `message = queue.pop()`.
    * Determine command from `message.text`.
    * Call the corresponding handler.
    * Send reply via `operator.send_text`.
    * Acknowledge processed messages.

Handlers return plain text not exceeding the Meshtastic limit; the host is responsible for splitting long responses across multiple packets.

#### handlers.mail

Implements minimal personal mailboxes.

* `handle_mail(message: BBSMessage) -> str`
    * Parses subcommands: list, read, send.
    * Stores messages under `data/mail/<user>/`.

#### handlers.board

Public bulletin board threads.

* `handle_board(message: BBSMessage) -> str`
    * Stores posts in `data/board/<thread>/`.

### Relationships with Meshtastic library

* `meshtastic.serial_interface.SerialInterface` provides the USB connection.
* `pubsub.pub.subscribe` feeds received packets into `BBSOperator.on_receive`.
* `SerialInterface.sendText` is used for outgoing replies.

The operator hides these details so that handlers and plugins interact only with `BBSMessage` objects and `send_text`.

### Extending phase 1

Developers can add new commands by placing modules in `service_host/handlers/` and calling `register_handler`.  Handlers can maintain state in `data/` or external stores.

## Phase 2 – Librarian chatbot & library

### Goals

* Retrieval‑augmented chatbot that answers questions from a local library.
* Multi‑part message support for longer answers.

### Implementation outline

* Add `librarian` plugin under `service_host/handlers/`.
* `handle_librarian(message: BBSMessage) -> list[str]`
    * Uses a local RAG pipeline to generate short text segments.
    * Returns a list of message parts; the service host loops over them when sending replies.
* Extend `ServiceHost.send_reply` to accept a list of strings for multi‑part messages.

Users may swap the RAG backend by providing an object with a `query(text: str) -> list[str]` interface.

## Phase 3 – Multi‑User Dungeon and games

### Goals

* Provide a simple MUD engine and additional games.
* Support persistent sessions.

### Implementation outline

* Create `mud` package under `service_host/handlers/` with a `GameSession` class.
* `GameSession` stores player location, inventory and pending output.
* `handle_mud(message: BBSMessage) -> str`
    * Loads or creates a `GameSession` for `message.sender_id`.
    * Interprets the command (look, move, talk).
    * Returns the resulting narrative text.
* Additional mini‑games follow the same pattern and register their own handlers.

Sessions are persisted under `data/mud/<player_id>.json` so users can resume later.

## Phase 4 – Federation & advanced features

### Goals

* Forward messages to remote BBS instances (store‑and‑forward).
* Add scheduling, sensors and other data feeds.

### Implementation outline

* Introduce `federation` module with functions:
    * `create_telegram(destination: str, payload: dict) -> Path`
    * `process_telegram(path: Path) -> None`
* `schedule` module for queued announcements:
    * `schedule_message(time: datetime, text: str, destination: str) -> None`
* Sensor integrations register periodic jobs that push notifications into the queue.

## Extending and customizing

The architecture encourages user customization:

* **Handlers** – New commands are simple functions that accept `BBSMessage` and return text.  Users drop a module in `handlers/` and register it.
* **Queue backend** – Implement the `MessageQueue` interface to switch between in‑memory, SQLite or distributed queues.
* **Plugins** – Complex features (Librarian, MUD, federation) live in separate modules that can be enabled or disabled.
* **Meshtastic options** – `BBSOperator` accepts additional keyword arguments forwarded to `SerialInterface` for advanced radio settings.

By adhering to small, focused functions and clear naming, developers can easily understand and extend the system while staying within the constraints of the Meshtastic network.

