import base64

from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory
from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout
from twisted.internet.task import deferLater


# noinspection PyArgumentList
class HermesExchangeProtocol(Protocol):
    def __init__(self):
        self.buffer = None
        self.b64_string = ""
        self.filehandle = None
        self.file = None
        self.state = "INIT"

    def auth(self, args: list):
        self.state = "AUTH"
        if args[0] == "1":
            print("Server has requested full authentication.")
        else:
            username = "."
            while not username.isalnum():
                username = input("Please set a username (only letters and numbers): ")
            self.transport.write(f"AUTH {username}\n".encode("utf-8"))

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
        with patch_stdout():
            user = prompt("Name of user which will recieve the file: ")
            self.file = prompt("Path to file: ")
        self.transport.write(f"WRITE {user};{self.file};220\n".encode("utf-8"))

    def list_users(self, args):
        print("Connected users are: ")
        for user in args:
            print(user)
        self.defer_main([])

    def wait_req(self, args):
        self.state = "WAIT"
        print("Waiting for other user to accept request...")

    def receive_req(self, args):
        print(f"User {args[0]} has requested to send a file: {args[1]}. Size: {args[2]}.")
        choice = input("Do you accept? [y/n] ")
        if choice == "y":
            self.state = "READ"
            self.filehandle = open(f"./output/{args[1]}", "wb")
            self.transport.write("ACCEPT\n".encode("utf-8"))
        else:
            self.transport.write("DENY\n".encode("utf-8"))

    def req_accept(self, args):
        self.state = "WRITE"
        print("Request accepted. Starting file transfer.")
        with open(self.file, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
            i = 0
            chunk = ""
            while i < len(data):
                chunk += data[i]
                if len(chunk) == 1024:
                    self.transport.write(f"DATA {chunk}\n".encode("utf-8"))
                    chunk = ""
                i += 1
            if chunk != "":
                print(chunk)
                self.transport.write(f"DATA {chunk}\n".encode("utf-8"))
        self.transport.write("EOF\n".encode("utf-8"))

    def req_deny(self, args):
        self.state = "MAIN"
        print("Request denied.")
        self.defer_main([])

    def save_data(self, args):
        self.b64_string += args[0]

    def close_data(self, args):
        self.filehandle.write(base64.b64decode(self.b64_string))
        self.filehandle.close()
        self.b64_string = ""
        self.state = "MAIN"
        print("File transfer complete.")
        self.defer_main([])

    def update_progress(self, args):
        #print(f"Transferred {args[0]}")
        pass

    def complete_write(self, args):
        self.state = "MAIN"
        print("File transfer complete.")
        self.defer_main([])

    def defer_main(self, args: list):
        deferLater(reactor, 0, self.main_loop)

    def main_loop(self):
        self.state = "MAIN"
        print("1. LIST users\n"
              "2. WRITE to user\n"
              "3. READ from user")
        with patch_stdout():
            selection = prompt("Select an option: ")
        self.handle_selection(selection)

    def handle_selection(self, selection):
        if selection == "1":
            self.transport.write("LIST\n".encode("utf-8"))
        elif selection == "2":
            self.write_req()
        elif selection == "3":
            print("Waiting for user to send request...")
            return

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

            print(f"{command}: {args}")

            if command == "INVALID":
                print("Sent invalid command for the current state.")

            state_machine = {
                "INIT": {
                    "AUTH": self.auth
                },
                "AUTH": {
                    "OK": self.defer_main,
                    "AUTHFAIL": self.auth_fail
                },
                "MAIN": {
                    "LIST": self.list_users,
                    "WAIT": self.wait_req,
                    "READ": self.receive_req
                },
                "WAIT": {
                    "ACCEPT": self.req_accept,
                    "DENY": self.req_deny
                },
                "READ": {
                    "DATA": self.save_data,
                    "EOF": self.close_data
                },
                "WRITE": {
                    "RECV": self.update_progress,
                    "OK": self.complete_write
                }

            }

            if self.state in state_machine.keys():
                if command in state_machine[self.state].keys():
                    state_machine[self.state][command](args)


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
    reactor.run()
