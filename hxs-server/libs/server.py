from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from .config import config


# noinspection PyArgumentList
class HermesExchangeProtocol(Protocol):
    def __init__(self, factory, users):
        self.buffer = None
        self.users: dict = users
        self.name = None
        self.state = "AUTH"
        self.requesting_user = None
        self.requested_user = None

    def connectionMade(self):
        print(f"Connection from {self.transport.getPeer().host}")
        data = f"AUTH {1 if config.auth_required else 0}\n"
        self.transport.write(data.encode("utf-8"))

    def auth(self, args):
        if config.auth_required and len(args) < 2:
            data = f"AUTHFAIL 1\n"
            self.transport.write(data.encode("utf-8"))
            self.transport.loseConnection()
            return
        elif config.auth_required and len(args) == 2:
            pass

        if args[0] in self.users.keys():
            data = f"AUTHFAIL 2\n"
            self.transport.write(data.encode("utf-8"))
            self.transport.loseConnection()
        else:
            self.name = args[0]
            self.users[args[0]] = self
            self.state = "MAIN"
            self.transport.write(b"OK\n")

    def list_users(self, args):
        users = ';'.join([user for user in self.users.keys() if user != self.name])
        data = f"LIST {users}\n"
        self.transport.write(data.encode("utf-8"))

    def write_req(self, args):
        self.state = "WREQ"
        self.requested_user = args[0]
        self.transport.write("WAIT\n".encode("utf-8"))
        self.users[args[0]].read_req([self.name, args[1], args[2]])

    def read_req(self, args):
        self.state = "RREQ"
        self.requesting_user = args[0]
        self.transport.write(f"READ {args[0]};{args[1]};{args[2]}\n".encode("utf-8"))

    def read_acc(self, args):
        self.users[self.requesting_user].state = "WRITE"
        self.state = "READ"
        self.users[self.requesting_user].transport.write("ACCEPT\n".encode("utf-8"))

    def read_deny(self, args):
        self.users[self.requesting_user].state = "MAIN"
        self.state = "MAIN"
        self.users[self.requesting_user].requested_user = None
        self.users[self.requesting_user].transport.write("DENY\n".encode("utf-8"))
        self.requesting_user = None

    def write(self, args):
        frags = args[0].split("#")
        self.transport.write(f"RECV {len(frags[0])}\n".encode("utf-8"))
        self.users[self.requested_user].transport.write(f"DATA {frags[0]}\n".encode("utf-8"))

    def eof(self, args):
        self.users[self.requested_user].state = "MAIN"
        self.state = "MAIN"
        self.users[self.requested_user].transport.write("EOF\n".encode("utf-8"))
        self.transport.write("OK\n".encode("utf-8"))
        self.users[self.requested_user].requesting_user = None
        self.requested_user = None

    def dataReceived(self, data):
        received = data.decode("utf-8")
        if self.buffer is not None:
            received = self.buffer + received
            self.buffer = None
        split_recieved = received.split("\n")
        if received[-1] != "\n":
            self.buffer = split_recieved[-1]
            split_recieved[-1] = ""

        for command in split_recieved:
            if command == "":
                continue
            fragments = command.split(" ")
            command = fragments[0]
            args = fragments[1].split(";") if len(fragments) > 1 else []

            print(f"{self.name} {command} {args}")

            state_machine = {
                "AUTH": {
                    "AUTH": self.auth
                },
                "MAIN": {
                    "LIST": self.list_users,
                    "WRITE": self.write_req
                },
                "RREQ": {
                    "ACCEPT": self.read_acc,
                    "DENY": self.read_deny
                },
                "WRITE": {
                    "DATA": self.write,
                    "EOF": self.eof
                }
            }

            if self.state in state_machine.keys():
                if command in state_machine[self.state].keys():
                    state_machine[self.state][command](args)
                else:
                    print(f"\n\n\nERROR: {command}\n\n\n")
                    self.transport.write("INVALID".encode("utf-8"))

    def connectionLost(self, reason):
        self.users.pop(self.name, None)


class HermesExchangeFactory(Factory):
    users = {}

    def buildProtocol(self, addr):
        return HermesExchangeProtocol(self, self.users)


def start_server():
    reactor.listenTCP(config.bind_port, HermesExchangeFactory(), interface=config.bind_ip)
    reactor.run(False)
