# Cyberpony Express Bulletin Board Service (BBS)

Welcome to the **Cyberpony Express BBS** project!  This repository will contain the code and documentation for the still-under-development text‑based bulletin‑board system that operates over the [Meshtastic](https://meshtastic.org) mesh‑networking platform.  It forms the digital‑postal backbone of the [Cyberpony Express](https://highdesertinstitute.org/guilds/lorekeepers/cyberpony-express/)  project—a free, encrypted mesh network built on LoRa radios that lets communities share messages and files when traditional Internet connections are unavailable.

## Why Cyberpony Express?

Conventional communication infrastructure is fragile. A single fiber cut or power outage can leave communities without access to vital information. Cyberpony Express solves this problem by creating a decentralized “digital postal service” built on inexpensive Meshtastic nodes. It allows people to send and receive messages, files and other data across a mesh of devices without relying on central servers. Anyone can host a node, and the network runs entirely off‑grid if needed.

## The role of the BBS

The **Bulletin Board Service (BBS)** is the heart of the Cyberpony Express.  It acts like an automated phone operator that:

* Provides a menu‑driven interface so users can **check messages, view public or private threads and talk to the librarian chatbot** by sending single‑letter commands.
* **Queues and forwards messages** between distant parts of the mesh, solving the *back‑haul problem* and allowing nodes that cannot directly hear each other to exchange data.
* Serves as the access point for **text‑based games (multi‑user dungeons)** and a **librarian chatbot** that can answer queries using a local library.
* Runs on low‑power hardware so it continues working in disasters; heavy processing is off‑loaded to a Raspberry Pi service host.

### Backhaul via IPFS and Tor

Cyberpony Express nodes are designed to **backhaul messages and synchronize BBS data using [IPFS](https://ipfs.tech) and the Tor network**.  Each BBS node can advertise itself on a distributed hash table via IPFS and then create an onion service through Tor to exchange data with peers.  This approach lets nodes find each other and relay messages **without exposing a public IP address**, and without relying on static IP assignments, DNS or any centralized oracle or hierarchical infrastructure.  Because IPFS handles content addressing and Tor provides privacy‑preserving routing, BBS operators can securely mirror bulletin boards and mail between distant networks even when they don’t share direct LoRa links.  Peers connect over Tor only long enough to exchange data and then return to purely LoRa operation, keeping the system decentralized and resilient.

While IPFS/Tor provides a critical backhaul, **the primary synchronization mechanism is always the LoRa mesh itself**.  Nodes attempt to exchange bulletins, mail and other state over the radio network whenever possible to preserve bandwidth and maintain decentralization.  The IPFS/Tor layer acts as a **fallback** for situations where long‑distance connections are not yet available—such as early stages of network deployment or isolated regions of the mesh.  In those cases, operators can still share data without static IP infrastructure, and once mesh connectivity improves the nodes will again prioritize direct LoRa synchronization.

### Architecture overview

```
User Node (T‑Beam Supreme)   ──▶  BBS Operator (T‑Beam Supreme) ──▶  Service Host (Raspberry Pi)
```

1. **User Node** – A Meshtastic node (e.g. T‑Beam Supreme) used by a participant to send and receive messages.
2. **BBS Operator** – A Meshtastic node running the BBS plugin.  It receives messages from users, interprets menu commands and queues requests for processing.
3. **Service Host** – A Raspberry Pi connected via USB to the BBS operator.  It runs Python services such as the **librarian chatbot** (retrieval‑augmented search over an offline library) and **multi‑user dungeon (MUD) games**.  These services process queued requests and send replies back over the mesh.

Because Meshtastic devices use **end‑to‑end encryption** and unique node IDs, responses can be delivered to the right user even when nodes are offline or moving.

### Influences and existing BBS projects

The Cyberpony Express BBS is inspired by several existing Meshtastic BBS implementations:

| Project                       | Highlights                                                                                                                                                                                                                                                                                                    | Lessons learned                                                                                                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **TC²‑BBS Mesh**              | Python‑based BBS designed for ultra‑low‑power microcontrollers; features a **mail system**, **bulletin boards**, **channel directory**, **statistics**, **Wall of Shame** (low‑battery devices) and a **fortune‑teller**.  Users interact by sending direct messages and selecting letter‑based menu options. | Demonstrated menu‑driven UX and how to run a BBS on battery‑powered microcontrollers.  However, custom hardware can be expensive and Python is not ideal for extremely constrained devices. |
| **VeggieVampire’s MeshBoard** | Simpler Python BBS that runs on a Raspberry Pi; includes **mini‑games** and **external mail services**.  A Tom’s Hardware story shows it playing games like Tic‑Tac‑Toe and an escape room over the mesh network.                                                                                             | Shows that a Pi‑based BBS can deliver engaging experiences (games) while maintaining simplicity.                                                                                            |
| **SpudGunMan’s Mesh Bot**     | A feature‑rich set of scripts offering **mail messaging**, **message scheduling**, **store‑and‑forward**, **built‑in games** (DopeWars, Lemonade Stand, BlackJack, etc.) and **AI integration** via a local large‑language model; it can even send weather alerts and other data over the mesh.               | Demonstrates advanced features (e.g. games, AI, data lookups) that could be integrated into Cyberpony Express in later phases.                                                              |

## Project Goals

1. **Open‑source, community‑maintained BBS** – provide a permissively licensed Python implementation that anyone can run on a T‑Beam Supreme and Raspberry Pi.
2. **Robust offline communications** – deliver basic messaging (public threads, private mail, channel directory), long‑distance relaying and store‑and‑forward capabilities.
3. **Knowledge access via the Librarian** – integrate a retrieval‑augmented chatbot that can search a local “Internet‑in‑a‑Box” library and answer user questions.
4. **Educational games and MUDs** – create a multi‑user dungeon engine accessible over the mesh.  MUDs will teach participants how to use the network and provide fun, off‑grid entertainment.
5. **Low‑power and resilient** – optimize the BBS operator to run on battery‑powered T‑Beam devices while off‑loading computation to the Raspberry Pi service host.

## Software Scope: Raspberry Pi Service Host

This repository focuses on developing the Python software that runs on the Raspberry Pi service host. In a typical deployment, a low‑power T‑Beam Supreme or similar LoRa device runs Meshtastic and the BBS operator plugin; it forwards user commands to the Raspberry Pi, which performs the heavy lifting (reading and writing mail, interacting with the librarian chatbot, running games and handling notifications) and sends replies back through the operator. While other parts of the Cyberpony Express (such as the Meshtastic firmware and radio hardware) live in their own repositories, this project encapsulates the logic for the service host, making it the main entry point for contributions that implement new BBS features.

The design goal is to keep the BBS operator on the T‑Beam as light as possible (interpreting single‑character commands, queueing requests and relaying responses) while allowing the Raspberry Pi to handle application logic in Python. By separating the concerns this way, developers can iterate quickly on the high‑level user experience without being constrained by the microcontroller’s limited resources.

### Menu System and User‑Interface Flow

The BBS user interface is menu‑driven and delivered via text messages over the mesh network. Every exchange between a user and the BBS is constrained by the 237‑character limit imposed by Meshtastic; messages that exceed this length must be split across multiple transmissions. Additionally, the Meshtastic app presents each incoming message in a separate chat bubble, so visual separation happens naturally. As a result, the BBS avoids drawing lines or other separators; instead, it simply sends a new message when a logical break is needed. A Markdown horizontal rule (---) may be used as an escape character inside a single message to indicate a separation if absolutely necessary, but the preferred approach is to send separate messages.

### Initial greeting and main menu

When a user first sends any message (even just “Hi”) to the BBS, the service responds with a welcome header containing contextual information (software version, timestamp, approximate location, number of active users, number of new messages and notifications, and battery status) followed by the main menu. Because of the character limit, this information may be sent as multiple messages. For example:

```
User: Hi

BBS: Cyberpony Express BBS v0.1
2025‑08‑01 2:30 PM
Sunny 80°
San Francisco, CA
25 active users
5 new messages
20 notifications
Battery: 86%

BBS: Main Menu:
1. Messages
2. Notifications
3. AI Chat
4. Human Chat (MUDs)
5. Weather
```

Here, the BBS has chosen to break the header and the menu into two messages to remain under the character limit. The absence of separators between the two messages is intentional; the chat bubbles themselves serve as separators.
Menu definitions

Each menu option leads to a sub‑menu or action. The current high‑level structure is:

1. Messages – View, send or manage personal mail. When selected, the BBS returns a Messages Menu listing options such as Read New, Read All, Send Message, Manage Threads and Return to Main. The Read New option shows a list of new messages (numbered) and invites the user to enter a number to read a specific message; after reading, the user may reply, delete or return to the list. The Send Message option prompts for the destination (by node ID or alias) and then the message body. At any point, sending 0 returns to the previous menu.
2. Notifications – View system notifications (e.g., channel announcements, battery warnings, network status). Selecting this option displays the most recent notifications (numbered) and allows the user to mark them as read or delete them. As with messages, entering 0 will return to the main menu3.
3. AI Chat – Talk to the Librarian chatbot. The user may send a question or request; the librarian responds with a concise answer (again, respecting the 237‑character limit and splitting across multiple messages if necessary). After the answer, the menu offers options like Ask Another Question or Return to Main. When a response requires multiple parts, the BBS sends them one after another, each clearly labelled (e.g., “1/3”, “2/3”, “3/3”) so users know when the answer is complete.
4. Human Chat (MUDs) – Enter the multi‑user dungeon environment. The BBS will switch the conversation into a text‑adventure mode where players explore a shared world, issue commands and interact with other players. A MUD Menu provides commands such as Look, Move, Inventory, Help and Return to Main. Returning to the main menu suspends the game session but does not delete it; players can resume later.
5. Weather – Request current weather or forecasts from the service host (when available). The menu may offer Current Conditions, Forecast and Return to Main.

Navigating menus

The BBS uses single‑character commands (numbers or letters) to navigate. When a menu is displayed, the user selects an option by sending the corresponding number. Within any sub‑menu, sending 0 returns to the previous menu; from the main menu, sending 0 exits the BBS session. If a user enters an invalid option, the BBS re‑displays the current menu with an error message (e.g., “Invalid selection. Please choose from the listed options.”). The BBS also supports shortcuts, such as sending M to jump directly back to the main menu from anywhere.
Message formatting guidelines

- Character limit: All responses must fit within 237 characters per message. When content exceeds this limit, split it into separate messages; do not rely on line breaks alone.
- No decorative separators: Use separate messages rather than horizontal rules or lines. If necessary, a --- sequence may denote a separation within a single message, but avoid overusing it.
- Stateful interactions: The BBS tracks each user’s current menu context so that it can interpret responses correctly. For example, after the BBS shows the Messages Menu, sending 1 triggers the Read New action rather than referring to the main menu.
-Graceful fallback: If the BBS does not understand a command or context is lost, it sends a friendly error message and redisplays the relevant menu.

By formalizing the menu system and message formatting as described above, we lay the groundwork for implementing the BBS logic in Python on the Raspberry Pi while ensuring a consistent, user‑friendly experience over the constrained LoRa mesh network.

## High Desert Institute & Community Resilience

The High Desert Institute (HDI) is a 501(c)(3) non‑profit dedicated to “building a foundation for the survival of humanity.” Its mission is to create off‑grid land projects, publish free libraries of knowledge and organize guilds that empower communities to live sustainably. HDI’s founders are raising funds to establish permaculture and mutual‑aid outposts in the high deserts of the American southwest; these sites will research, develop and distribute free, open‑source solutions to basic needs like housing and off‑grid infrastructure. The organization operates transparently—every donated dollar supports the mission—and publishes everything it learns so others can replicate its work.

### The Library and the Librarian

HDI’s library project aims to publish a vast, free, open‑source library that contains the knowledge required to live well off‑grid. The idea originated when one of the intentional communities HDI helped build requested a way to host private intranets with useful information. HDI’s library will be freely accessible to anyone and will include both the institute’s own findings and curated content from other sources. Within the BBS, this library is accessed through the Librarian chatbot, which uses retrieval‑augmented generation (RAG) to search the local library and answer questions. By embedding a searchable library in the off‑grid mesh, the project turns the BBS into more than just a messaging system—it becomes a knowledge hub for communities during disasters.

### How Cyberpony Express fits into HDI’s mission

HDI partners with Burners Without Borders and the Multiverse School to build the Cyberpony Express—a free, secure, public mesh network using Meshtastic nodes. This network connects HDI outposts and intentional communities without relying on the fragile infrastructure of the Internet or cell towers. It is therefore vital disaster‑response infrastructure: by maintaining communications when conventional networks fail, the Cyberpony Express helps communities stay safe and coordinated during emergencies. The BBS described in this repository is the core software service that runs atop Cyberpony Express, providing a digital postal service, a library interface and text‑based games. Together, these components support HDI’s broader goal of building resilient, sustainable communities through open knowledge, decentralized communication and mutual aid.

### Guilds and community development

HDI organizes guilds—semi‑autonomous groups that focus on specific aspects of community development. Guilds can fundraise and make decisions independently, and are encouraged to grow beyond HDI to operate all over the world. The Librarians’ Guild, for instance, is spearheading the development of the Cyberpony Express BBS and the off‑grid library. By fostering guilds, HDI builds a network of practitioners who can share knowledge, design new tools and support one another in cultivating resilient, sustainable and disaster‑ready communities.

## Roadmap

Below is a high‑level roadmap for the Cyberpony Express BBS.  We welcome contributions and feedback!

### 🚀 Phase 1 – Core BBS (Current)

* **Define architecture and repository structure.**
* **Implement BBS operator** for Meshtastic (runs on Raspberry Pi or a second ESP32, connects to T-Beam).  Handles message parsing and queueing.
* **Develop service‑host framework** (Python) that listens to the queue, processes commands and sends responses via the operator.
* **Provide basic mail and bulletin board functionality** inspired by TC²‑BBS (mailboxes, public and private threads, channel directory, statistics and a simple “wall of shame” for low‑battery nodes).
* Write comprehensive documentation and installation scripts (in progress).

### 📚 Phase 2 – Librarian Chatbot & Library Integration

* Implement Librarian chatbot using retrieval‑augmented generation (RAG).  The bot should answer questions from a local “Internet‑in‑a‑Box” library, plus other local libraries node maintainers can choose to include.
* Add multi‑part message support for longer answers and summarization.
* Allow offline search of curated datasets (e.g. prepared survival guides, local weather data, etc.).

### 🕹️ Phase 3 – Multi‑User Dungeon and Games

* Build MUD engine that can run simple text adventures over the mesh.  Start with small scenarios; integrate with librarian data to teach network usage.
* Port classic games (e.g. tic‑tac‑toe, Blackjack) and add new ones inspired by VeggieVampire and SpudGunMan’s implementations.
* Enable game persistence and multi‑player sessions.

### 🌐 Phase 4 – Federation & Advanced Features

* Support multi‑hop BBS linking to allow separate BBS nodes to sync messages and bulletins, creating a global Cyberpony Express network.
* Add store‑and‑forward and scheduling capabilities (message scheduling, recurring announcements) similar to Mesh Bot.
* Integrate sensors and data feeds (weather alerts, air quality, satellite passes) to provide real‑time information to users.
* Experiment with other local AI models for on‑device inference and summarization.

## Contributing

We encourage pull requests and issue reports! This project is community‑driven; feel free to propose features, report bugs or improve documentation.
