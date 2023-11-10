import datetime
import json
import os
import subprocess
from collections import deque
from queue import Queue
from threading import Thread
from typing import List, Dict


class Device:
    def __init__(self, address, label, last_seen, online, protocol):
        self.address = address
        self.label = label
        self.last_seen = last_seen
        self.online = online
        self.protocol = protocol
        self.port_name = self.address if self.is_serial_device() else f"{self.address}"

    def is_network_device(self):
        return self.protocol == 'network'

    def is_serial_device(self):
        return self.protocol == 'serial'

    def to_dict(self):
        return {
            'address': self.address,
            'label': self.label,
            'last_seen': self.last_seen,
            'online': self.online,
            'protocol': self.protocol,
            'port_name': self.port_name,
        }


thread: Thread | None
board_list: Dict[str, Device]
queue: Queue
network_boards_queue: deque


def update_board_list(event):
    global board_list
    event_type = event['eventType']
    port_info = event['port']
    label = port_info['address']
    print(event_type, ' ', label)

    if event_type == 'add' and label not in board_list:
        board_list[label] = create_device(port_info)
        if board_list[label].is_network_device():
            network_boards_queue.append(board_list[label])
    elif event_type == 'add':
        board_list[label].online = True
        board_list[label].last_seen = datetime.datetime.now()
    elif event_type == 'remove' and label in board_list:
        board_list[label].online = False


arduino_cli = os.getenv("ARDUINO_CLI")


def arduino_cli_watcher():
    with subprocess.Popen([arduino_cli, "board", "list", "-w", "--format", "json"],
                          stdout=subprocess.PIPE,
                          bufsize=1,
                          universal_newlines=True) as proc:
        current_json = ''
        for line in proc.stdout:
            current_json += line
            if line.startswith('}'):
                event = json.loads(current_json)
                update_board_list(event)
                current_json = ''
        proc.stdout.close()


def start_watching():
    global thread, board_list, queue, network_boards_queue
    print('Started arduino board watcher')
    thread = Thread(target=arduino_cli_watcher)
    thread.start()
    board_list = {}
    queue = Queue()
    network_boards_queue = deque()


def get_board_list() -> List[Device]:
    return list(board_list.values())


def get_active_serial_boards() -> List[Device]:
    return list(filter(lambda board: board.is_serial_device(), board_list.values()))


def get_next_network_device() -> Device | None:
    if len(network_boards_queue) == 0:
        return None
    network_boards_queue.rotate(1)
    return network_boards_queue[0]


def create_device(json: dict) -> Device:
    return Device(json['address'], json['label'], datetime.datetime.now(), True, json['protocol'])
