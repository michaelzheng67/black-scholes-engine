'''
Protocol to fetch data from tcp connection. The main issue currently is that TCP byte stream
inherently does NOT delimit messages. Thus, this collection of functions hopes to do this and
abstract away that work from the user.
'''
import struct
import json


'''
Given a client socket connection, return client data.
Note: data is of variable size, so each message is prefixed with the message
length. Moreover, we buffer received data to split it appropriately (received
as byte stream).
'''
def accept_json_data(conn):

    while True:
        length_prefix = conn.recv(4)
        if not length_prefix:
            return

        message_length = struct.unpack('!I', length_prefix)[0]
        message = b""
        buffer = b"" # store for case of multiple logical messages in single chunk

        while len(message) < message_length:
            chunk = conn.recv(4096)
            if not chunk:
                break

            buffer += chunk
            if len(buffer) >= message_length:
                fetch_size = message_length - len(message)
                message += buffer[: fetch_size]
                buffer = buffer[fetch_size :]

        yield json.loads(message.decode('utf-8'))


'''
Given a connection, sends data.
Note: data sent as prefix + payload.
'''
def send_data(conn, data):
    json_data = json.dumps(data).encode('utf-8')
    message_length = struct.pack('!I', len(json_data))
    conn.sendall(message_length + json_data)
