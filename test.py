from threading import Thread

from client import KeyValueClient
from server import create_server


def test():
    server = create_server()

    thread = Thread(target=server.serve_forever)
    thread.start()

    host, port = server.server_address
    client = KeyValueClient(host, port)

    # {}
    test_values = client.get_keys(["test"])
    assert test_values is None, f"Should be empty: {test_values}"

    # {"test": "data"}
    test_data = {"test": "data"}
    assert client.set_keys(test_data), "Can't set keys"

    # {"test": "data"}
    response_1 = client.get_keys(["test"])
    assert response_1 == test_data, f"Data not equal: {response_1} != {test_data}"

    # {"test": "data"}
    response_2 = client.get_keys(["test", "test2"])
    assert response_2 is None, f"Should be empty: {response_2}"

    # {"test": "data", "test2": ["array"]}
    test_data["test2"] = ["array"]
    assert client.set_keys(test_data), "Can't set keys"

    # {"test": "data", "test2": ["array"]}
    response_3 = client.get_keys(["test", "test2"])
    assert response_3 == test_data, f"Data not equal: {response_3} != {test_data}"

    # {"test2": ["array"]}
    test_data.pop("test")
    assert client.delete_keys(["test"]), "Can't delete keys"

    # {"test2": ["array"]}
    response_4 = client.get_keys(["test", "test2"])
    assert response_4 is None, f"Should be empty: {response_4}"

    # {"test2": ["array"]}
    response_5 = client.get_keys(["test2"])
    assert response_5 == test_data, f"Data not equal: {response_5} != {test_data}"

    # {"test2": ["array"]}
    response_6 = client.get_all_keys()
    assert response_6 == list(test_data), f"Data not equal: {response_6} != {test_data}"

    print("Tests OK")

    server.shutdown()
    thread.join()


if __name__ == "__main__":
    test()
