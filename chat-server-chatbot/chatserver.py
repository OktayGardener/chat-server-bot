import math
import struct
import socket
import select
import threading

_HOST = '127.0.0.1'  # localhost
_PORT = 10000


class ChatServer(threading.Thread):
    """
    Defines the chat server as a thread
    """
    MAX_WAITING_CONNECTIONS = 10
    RECV_BUFFER = 4096  # size of message
    RECV_MSG_LEN = 4  # size of placeholder in bytes

    def __init__(self, host, port):
        """Initializes a new ChatServer.

        Args:
            host: Host server binds to.
            port (int): Port server binds to.
        """
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.connections = []
        self.running = True

    def _bind_socket(self):
        """Creates server socket and binds to given host & port.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.MAX_WAITING_CONNECTIONS)
        self.connections.append(self.server_socket)

    def _send(self, socket, message):
        """Sends a message with a 4-byte prefix.
        Args:
            socket: Socket to send to.
            message (string): Message to be sent.
        """
        # Packs message with 4 leading bytes representing the msg length
        message = struct.pack('>I', len(message)) + message
        socket.send(message)

    def _receive(self, socket):
        """Receives an incoming message from a client and unpacks it.
        Args:
            socket: Host server binds to.
        Returns:
            data: Unpacked message.
        """
        data = None

        total_length = 0

        while total_length < self.RECV_MSG_LEN:
            message_len = socket.recv(self.RECV_MSG_LEN)
            total_length += len(message_len)

        if message_len:
            data = ''
            message_len = struct.unpack('>I', message_len)[0]
            total_data_length = 0

            while total_data_length < message_len:
                part = socket.recv(self.RECV_BUFFER)

                if not part:
                    # No expected part, throw error?
                    data = None
                    break
                else:
                    # Merge
                    data += part
                    total_data_length += len(part)
            return data

    def _broadcast(self, client_socket, client_message):
        """ Broadcasts a message to all other sockets
            except for server and sender sockets.
        Args:
            client_socket (socket): sender socket
            client_message (string): message to broadcasted
        """
        for socket in self.connections:  # remove from list instead?
            if socket != self.server_socket and socket != client_socket:
                try:
                    socket.send(client_message)
                    # self._send(socket, client_message)
                except:
                    print("socket error: %s") % (socket.error)
                    print("closing and removing socket")
                    socket.close()
                    if socket in self.connections:
                        self.connections.remove(socket)

    def _run_server(self):
        """Main runner for the server.
        """
        while self.running:
            try:
                ready_to_read, ready_to_write, in_error = select.select(self.connections, [], [], 0)
            except socket.error:
                print("socket error ready to read etc")
                continue
            else:
                for socket in ready_to_read:
                    if socket == self.server_socket:
                        try:
                            client_socket, client_address = self.server_socket.accept()
                        except socket.error:
                            print("error when trying to accept, %s") % socket.error
                            break
                        else:
                            self.connections.append(client_socket)
                            print "Client (%s, %s) connected" % client_address
                            self._broadcast(
                                client_socket, "\n[%s - %s] entered the chatroom\n" % client_address
                            )
                    else:
                        try:
                            data = socket.recv(self.RECV_BUFFER)
                            if data:
                                print("Broadcasting data")
                                self._broadcast(
                                    socket, "\r" + '<' + str(socket.getpeername()) + '> ' + data
                                )
                        except:
                            self._broadcast(
                                socket, "\n Client (%s, %s) is not reachable\n" % client_address
                            )
                            print("\n Client (%s, %s) is not reachable\n")
                            socket.close()
                            self.connections.remove(socket)
                            continue
        self.stop()

    def run(self):
        """Given a host and port, bind socket and run server.
        """
        self._bind_socket()
        self._run_server()

    def stop(self):
        """Stops the server by setting the running flag before closing connection.
        """
        self.running = False
        self.server_socket.close()


def main():
    """
    The main function of the program. It creates and runs a new ChatServer.
    """
    chat_server = ChatServer(_HOST, _PORT)
    chat_server.start()
    print("Chat server started. Hosting at %s on port %s") % (_HOST, _PORT)


if __name__ == '__main__':
    """The entry point of the program. It simply calls the main function.
    """
    main()
