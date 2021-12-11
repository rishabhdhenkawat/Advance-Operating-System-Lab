import socket
import json
import _thread
import time
import random
import os
import tqdm
import threading

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"


class Error:
    commandInputError = Exception("Please enter correct command")
    portInputError = Exception("Please enter correct port number")
    controllerError = Exception("Controller Error. Try After Sometime")
    createRoomError = Exception("Error in creating the room")


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.flag = 0

    def createSocket(self, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, port))
        return client

    def decode(self, value):
        return value.decode('ascii')

    def encode(self, value):
        return value.encode('ascii')

    def listen(self, client):
        while True:
            data = client.recv(1024)
            if not data:
                break
            print(self.decode(data))
        client.close()
        exit(0)

    def send(self, client):
        while True:
            message = input("")
            self.flag += 1
            if(message == "./leave"):
                break
            client.send(self.encode(message))

        client.send(self.encode(message))
        self.flag += 1
        client.close()
        exit(0)

    def rec_file(self, client):
        received = client.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        # remove absolute path if there is
        filename = os.path.basename(filename)
        # convert to integer
        filesize = int(filesize)
        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(
            filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = client.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is receivedc vb b+
                    # file transmitting is done
                    break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
        progress.update(len(bytes_read))

    def joinChatRoom(self, port):
        try:
            client = self.createSocket(port)
            name = input("Enter Name : ")
            client.send(name.encode('ascii'))
            _thread.start_new_thread(self.listen, (client,))
            _thread.start_new_thread(self.send, (client,))
            while True:
                continue
        except Exception as e:
            print(e)
            self.joinChatRoom(port+1)

    def start(self):
        client = self.createSocket(self.port)
        while True:
            try:
                command = input("Enter command : ")
                if(command == "./join"):
                    port = input("Enter port of 5 digits: ")
                    assert(len(port) == 5)
                    client.close()
                    self.joinChatRoom(int(port))
                    break
                elif(command == "./createRoom"):
                    client.send(self.encode(command))
                    reply = client.recv(1024)
                    if not reply:
                        raise Error.controllerError
                        continue
                    result = json.loads(str(self.decode(reply)))
                    if(result["status"] == 200):
                        if(result["type"] == "creation"):
                            client.close()
                            print(result["message"])
                            self.joinChatRoom(result["port"])
                            break
                    else:
                        raise Error.createRoomError
                else:
                    raise Error.commandInputError
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    client = Client('127.0.0.1', 12343)
    client.start()
