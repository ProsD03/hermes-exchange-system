from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout


class HermesExchangeProtocol(Protocol):
    def __init__(self):
        self.state = "INIT"
    def dataReceived(self, data):
        command = data.decode("utf-8")
        fragments = command.split(" ")
        command = fragments[0]
        args = fragments[1].split(";") if len(fragments) > 1 else []

        if self.state == "INIT":
            if command == "AUTH":
                self.state = "AUTH"
                if args[0] == "1":
                    print("Server has requested full authentication.")
                else:
                    username = "."
                    while not username.isalnum():
                        username = input("Please set a username (only letters and numbers): ")
                    data = f"AUTH {username}"
                    self.transport.write(data.encode("utf-8"))
        elif self.state == "AUTH":
            if command == "OK":
                print("Authentication successful.")
                print("Select operation: ")
            elif command == "AUTHFAIL":
                if args[0] == "1":
                    print("Authentication failed: Wrong or Missing password")
                    reactor.stop()
                elif args[0] == "2":
                    print("Authentication failed: Username already in use")
                    reactor.stop()


class HermesExchangeFactory(ClientFactory):
    def buildProtocol(self, addr):
        print(f'Connected to {addr.host}:{addr.port}')
        return HermesExchangeProtocol()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)

def start_client(host: str, port: int):
    reactor.connectTCP(host, port, HermesExchangeFactory())
    reactor.run(False)