from libs.config import config
from libs import server
from yaspin import yaspin
from yaspin.spinners import Spinners
from threading import Thread

print(f"Welcome to the Hermes Exchange System Server.")
with yaspin(Spinners.dots) as sp:
    sp.text = f"Loading configuration file..."
    if config.load_config("./config.toml"):
        sp.text = ""
        sp.ok(f"✔ Configuration file loaded!")
    else:
        sp.text = ""
        sp.ok(f"✘ Configuration file not found! Using default configuration.")

with yaspin(Spinners.dots) as sp:
    sp.text = f"Trying to bind on {config.server.bind_ip}:{config.server.bind_port}..."
    server.bind_server()
    sp.text = ""
    sp.ok(f"✔ Server bound and listening on {config.server.bind_ip}:{config.server.bind_port}.")
server.start_server()