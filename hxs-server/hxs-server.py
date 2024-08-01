from libs.config import config
from libs import server
from yaspin import yaspin
from yaspin.spinners import Spinners
from threading import Thread

print(f"Welcome to the Hermes Exchange System Server.")
with yaspin(Spinners.dots) as sp:
    sp.text = f"Trying to bind on {config.bind_ip}:{config.bind_port}..."
    server_thread = Thread(target=server.start_server, args=())
    server_thread.start()
    sp.text = ""
    sp.ok(f"✔ Server bound and listening on {config.bind_ip}:{config.bind_port}.")
server_thread.join()