import sys
import socket
import select
import argparse
import re
from bot import *

class Client(object):
    RECV_BUFFER = 4096

    def __init__(self, host, port, bot=None):
        self.host = host
        self.port = port
        self.username = ''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.bot = bot

    def send_username():
        return "<%s, %s>" % (self.host, self.username)

    def set_username(self):
        if not self.bot:
            self.username = raw_input("Enter a username: ")
        else:
            self.username = "adambot"

    def send_bot_message(self, data):
        message = self.bot.response(data)
        self.socket.send(message + '\n')

    def send_message(self):
        message = sys.stdin.readline()
        if not self.bot:
            self.socket.send(message)
        sys.stdout.write('%s > ' % self.username)
        sys.stdout.flush()

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
        except:
            print("Connection error")
            sys.exit()
        else:
            print 'Connected to chatroom. Welcome! Try talking to the adambot, @adambot sentence'
            self.set_username()
            sys.stdout.write('%s > ' % self.username)
            sys.stdout.flush()
        while True:
            socket_list = [sys.stdin, self.socket]
            read, write, err = select.select(socket_list, [], [])

            for sock in read:
                if sock == self.socket:
                    data = sock.recv(self.RECV_BUFFER)
                    if not data:
                        print("\n Disconnected from chat server.")
                        sys.exit()
                    else: # recieve messages
                        sys.stdout.write(data)
                        # check for bot message and reply instantly
                        if self.bot and bot_message(data):
                            self.send_bot_message(data)
                        sys.stdout.flush()
                        sys.stdout.write('%s > ' % self.username)
                        sys.stdout.flush()
                else: # sending messages
                    self.send_message()


def validate_args(host, port):
    if host != "localhost":
        try:
            socket.inet_aton(host)
        except socket.error:
            print("Bad IP Adress")
            return False

    if not re.findall(r'[0-9]+', str(port))[0]:
        print("Bad port number")
        return False
    return True

def bot_message(message):
    if "@adambot" in message:
        return True
    return False

def load_intents():
    with open(INTENT_JSON) as json_data:
        return json.load(json_data)

def loadbot():
    intents = load_intents()
    bot = Bot(intents)
    bot.load_model()
    return bot


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('host', metavar='host', nargs='+', help='host ip (ipv4 adress)')
    parser.add_argument('port', metavar='port', type=int, nargs='+', help='port number')
    parser.add_argument('--bot', help='Makes this client an adambot', action='store_true')

    args = parser.parse_args()
    host, port = args.host[0], args.port[0]
    if not validate_args(host, port):
        sys.exit()

    if args.bot:
        bot = loadbot()
        client = Client(host, port, bot)
    else:
        client = Client(host, port)

    client.connect()


if __name__ == '__main__':
    sys.exit(main())
