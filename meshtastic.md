# Connecting Cyberpony Express BBS to a Meshtastic Device

This guide explains how the Python service host for the Cyberpony Express BBS
communicates with a Meshtastic radio over a USB cable.  It covers hardware setup,
required Python functions, example return values, and the path a message takes
through the stack.

## 1. Hardware prerequisites

1. **Meshtastic node** (e.g. T‑Beam, T‑Deck, LILYGO T‑Echo) flashed with the
   official [Meshtastic firmware](https://meshtastic.org/docs/firmware/flashing/).
2. **USB cable** connecting the radio to the computer or Raspberry Pi running the
   BBS service host.
3. Optional: `ls /dev/ttyUSB*` or `dmesg | tail` to determine the serial device
   path (usually `/dev/ttyUSB0` or `/dev/ttyACM0`).

## 2. Install the Meshtastic Python library

```bash
pip install meshtastic pubsub
```

The BBS uses the `meshtastic` package to talk to the radio and the `pubsub`
package to receive asynchronous events when packets arrive.

## 3. Opening the serial connection

```python
from meshtastic.serial_interface import SerialInterface

# Automatically connects on creation.  Use devPath to specify the USB port.
iface = SerialInterface(devPath="/dev/ttyUSB0")
```

`SerialInterface` constructor signature:
`SerialInterface(devPath=None, debugOut=None, noProto=False, connectNow=True, noNodes=False)`

* Returns: a `SerialInterface` instance representing the link to the radio.
* If `connectNow=False` is supplied, call `iface.connect()` later to establish
  the link.
* Call `iface.close()` when finished to release the USB port.

## 4. Querying device information

```python
info = iface.getMyNodeInfo()
print(info)
```

`getMyNodeInfo()` returns a dictionary for the local radio. Example:

```python
{
    'num': 287421444,              # numeric node ID
    'id': '!4a8f3e2d',             # text node ID
    'user': {
        'longName': 'BBS Operator',
        'shortName': 'BBS'
    },
    'hardware': 'TBEAM'
}
```

Other useful methods:

| Method | Description | Return type | Example |
| ------ | ----------- | ----------- | ------- |
| `getMyUser()` | Current user record for the radio. | `dict` | `{'id': '!4a8f3e2d', 'longName': 'BBS Operator', ...}` |
| `getNode(node_id)` | Node info for a specific ID or number. | `dict` | `iface.getNode('!abcd1234')` → `{'user': {...}, 'position': {...}}` |
| `getPublicKey()` | Local node’s public key for encrypted messaging. | `bytes` | `b'\x12\x83\x9f...'` |

## 5. Receiving packets

Meshtastic uses a publish–subscribe model.  Subscribe to `meshtastic.receive`
topics to act on incoming packets.

```python
from pubsub import pub

def on_receive(packet, iface):
    text = packet.get('decoded', {}).get('text', '')
    sender = packet.get('from')
    print(f"{sender} → {text}")

# Receive all packets or a specific subtype such as receive.text
pub.subscribe(on_receive, "meshtastic.receive.text")
```

The `packet` argument is a dictionary.  Example structure for a text message:

```python
{
    'from': 287421444,
    'to': 4294967295,
    'id': 17179870272,
    'decoded': {
        'portnum': 'TEXT_MESSAGE_APP',
        'payload': b'Hello BBS',
        'text': 'Hello BBS'
    }
}
```

## 6. Sending messages

```python
# Broadcast a message to the mesh
packet = iface.sendText("Cyberpony Express online!", destinationId="^all")
print(packet["id"])
```

`sendText(text, destinationId="^all", wantAck=False, wantResponse=False,
portNum=None, replyId=None)`

* Returns: the packet dictionary that was queued for transmission.  The `id`
  field can be used with `waitForAckNak(packet['id'])` to confirm delivery.

To send binary payloads or protobufs use `sendData(data, destinationId="^all",
portNum=None, wantAck=False, wantResponse=False, onResponse=None,
channelIndex=None, hopLimit=None, replyId=None)`.  It returns a packet dict
just like `sendText`.

## 7. Message flow through the stack

1. **User Node → LoRa** – A user’s Meshtastic device sends a text command.
2. **BBS Operator (T‑Beam)** – The radio connected to the BBS receives the
   packet over LoRa and forwards it via USB serial.
3. **Service Host (Raspberry Pi)** – The Python process running this project
   uses `SerialInterface` to parse the packet.  The registered `pub.subscribe`
   handler hands the message to the BBS logic.
4. **BBS processing** – The service determines an appropriate reply (menu,
   chatbot result, game output, etc.).
5. **Outgoing message** – The reply is sent back over the mesh with
   `sendText()` (or `sendData()` for binary/protobuf messages).
6. **LoRa → Recipient** – The Meshtastic firmware transmits the packet over
   radio and the user node displays the response.

The following minimal program exercises the full path:

```python
from meshtastic.serial_interface import SerialInterface
from pubsub import pub

def on_receive(packet, iface):
    print(f"RX from {packet['from']}: {packet.get('decoded', {}).get('text')}")
    iface.sendText("Message received!", destinationId=packet['from'])

pub.subscribe(on_receive, "meshtastic.receive.text")
iface = SerialInterface(devPath="/dev/ttyUSB0")
print("Connected to", iface.getMyNodeInfo()['user']['longName'])
```

## 8. Closing the connection

Call `iface.close()` to stop the reader thread and release the serial port when
you shut down the BBS.

---

By following the steps above, the Cyberpony Express BBS can communicate with a
Meshtastic device, process user commands and send responses back through the
mesh network.
