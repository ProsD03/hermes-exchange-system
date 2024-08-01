from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from .config import config


# noinspection PyArgumentList
class HermesExchangeProtocol(Protocol):
    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "AUTH"

    def connectionMade(self):
        print(f"Connection from {self.transport.getPeer().host}")
        data = f"AUTH {1 if config.auth_required else 0}"
        self.transport.write(data.encode("utf-8"))

    def dataReceived(self, data):
        print(data.decode("utf-8"))


class HermesExchangeFactory(Factory):
    users = {}

    def buildProtocol(self, addr):
        return HermesExchangeProtocol(self, self.users)


def start_server():
    reactor.listenTCP(config.bind_port, HermesExchangeFactory(), interface=config.bind_ip)
    reactor.run(False)
