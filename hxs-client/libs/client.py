from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from sys import stdout


# noinspection PyArgumentList
class 0HermesExchangeProtocol(Protocol):
    def __init__(self):
        self.state = "INIT"

    def auth(self, args: list):
        self.state = "AUTH"
        if args[0] == "1":
            print("Server has requested full authentication.")
        else:
            username = "."
            while not username.isalnum():
                username = input("Please set a username (only letters and numbers): ")
            data = f"AUTH {username}"
            self.transport.write(data.encode("utf-8"))

    def auth_fail(self, args: list):
        if args[0] == "1":
            print("Authentication failed: Wrong or Missing password")
            self.transport.loseConnection()
            reactor.stop()
        elif args[0] == "2":
            print("Authentication failed: Username already in use")
            self.transport.loseConnection()
            reactor.stop()

    def write_req(self):
        user = input("Name of user which will recieve the file: ")
        file = input("Path to file: ")
        self.transport.write(f"WRITE {user};{file};220".encode("utf-8"))

    def main_loop(self, args: list):
        self.state = "MAIN"
        print("1. LIST users\n"
              "2. WRITE to user\n"
              "3. READ from user")
        selection = input("Select an option: ")
        if selection == "1":
            self.transport.write("LIST".encode("utf-8"))

    def list_users(self, args):
        print("Connected users are: ")
        for user in args:
            print(user)
        self.main_loop([])

    def wait_req(self,args):
        self.state = "WAIT"
        print("Waiting for other user to accept request...")

    def dataReceived(self, data):
        command = data.decode("utf-8")
        fragments = command.split(" ")
        command = fragments[0]
        args = fragments[1].split(";") if len(fragments) > 1 else []

        stateMachine = {
            "INIT": {
                "AUTH": self.auth
            },
            "AUTH": {
                "OK": self.main_loop,
                "AUTHFAIL": self.auth_fail
            },
            "MAIN": {
                "LIST": self.list_users,
                "WAIT": self.wait_req,
                "READ": None
            },
            "WAIT": {
                "ACCEPT": None,
                "DENY": None
            },
            "READ": {
                "DATA": None,
                "EOF": None
            }
        }

        stateMachine[self.state][command](args)


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
