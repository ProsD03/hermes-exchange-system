from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from .config import config


# noinspection PyArgumentList
class HermesExchangeProtocol(Protocol):
    def __init__(self, factory, users):
        self.users = users
        self.name = None
        self.state = "AUTH"

    def connectionMade(self):
        print(f"Connection from {self.transport.getPeer().host}")
        data = f"AUTH {1 if config.auth_required else 0}"
        self.transport.write(data.encode("utf-8"))

    def dataReceived(self, data):
        command = data.decode("utf-8")
        fragments = command.split(" ")
        command = fragments[0]
        args = fragments[1].split(";") if len(fragments) > 1 else []

        if self.state == "AUTH":
            if command == "AUTH":
                if config.auth_required and len(args) < 2:
                    data = f"AUTHFAIL 1"
                    self.transport.write(data.encode("utf-8"))
                    return
                elif config.auth_required and len(args) == 2:
                    pass

                if args[0] in self.users.keys():
                    data = f"AUTHFAIL 2"
                    self.transport.write(data.encode("utf-8"))
                else:
                    self.name = args[0]
                    self.users[args[0]] = self
                    self.state = "MAIN"
                    self.transport.write(b"OK")


class HermesExchangeFactory(Factory):
    users = {}

    def buildProtocol(self, addr):
        return HermesExchangeProtocol(self, self.users)


def start_server():
    reactor.listenTCP(config.bind_port, HermesExchangeFactory(), interface=config.bind_ip)
    reactor.run(False)
