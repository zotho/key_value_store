import argparse
import json
import requests
from threading import Thread

from server import create_server


class KeyValueClient:
    def __init__(self, host, port):
        self.url = f"http://{host}:{port}"
        self.session = requests.Session()

    def get_keys(self, keys):
        response = self.session.get(self.url, params={"key": keys})
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_all_keys(self):
        response = self.session.get(f"{self.url}/keys")
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def set_keys(self, data):
        response = self.session.post(self.url, data=json.dumps(data))
        return response.status_code == 200

    def delete_keys(self, keys):
        response = self.session.delete(self.url, data=json.dumps({"key": keys}))
        return response.status_code == 200


def init_server(host=None, port=None):
    if host and port:
        server = create_server(host, port)
    else:
        server = create_server()

    thread = Thread(target=server.serve_forever)
    thread.start()

    host, port = server.server_address
    return host, port, server, thread


def main(host=None, port=None, noserver=False):
    client = KeyValueClient(host, port)

    print(
        f"Client for key-value server (http://{host}:{port}):\n"
        "g <key, ...> - Get keys\n"
        "l - Get all keys\n"
        "s <key=value, ...> - Set keys\n"
        "d <key, ...> - Delete keys\n"
        "e - Exit (also Ctrl-C and Ctrl-D)"
    )
    while True:
        try:
            command, whitespace, data = input("\n").partition(" ")
        except (KeyboardInterrupt, EOFError):
            break

        if not whitespace and command not in ("l", "e"):
            continue

        if command == "g":
            keys = [key.strip() for key in data.split(",")]
            response = client.get_keys(keys)
            print(response or f"Error! No keys: {keys}")

        if command == "l":
            response = client.get_all_keys()
            print(response if response is not None else "Error!")

        elif command == "s":
            pairs = [pair.strip().partition("=") for pair in data.split(",")]
            if not all(equal_char for _, equal_char, _ in pairs):
                print("Error! Can't parse data")
                continue

            data = {key: value for key, _, value in pairs}
            response = client.set_keys(data)
            print("OK" if response else "Error!")

        elif command == "d":
            keys = [key.strip() for key in data.split(",")]
            response = client.delete_keys(keys)
            print("OK" if response else "Error!")

        elif command == "e":
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Host for client")
    parser.add_argument("--port", help="Port for client", type=int)
    parser.add_argument(
        "--noserver",
        help="No initialize server (You must set host and port)",
        action="store_true",
    )
    args = parser.parse_args()

    server = None
    thread = None

    host = args.host
    port = args.port

    if not args.noserver:
        host, port, server, thread = init_server(host, port)
    elif host is None and port is None:
        raise ValueError("You must set host and port if no server (See --help)")

    try:
        main(host, port)
    except requests.exceptions.ConnectionError:
        print("Server is offline. Try later")

    if server and thread:
        server.shutdown()
        thread.join()
