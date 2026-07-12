import os

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv("my.env", True), verbose=True)


USE_PROXY = os.environ.get("use_proxy") == "True"

TG_PROXY = {
    "scheme": os.environ.get("tg_proxy_scheme", "socks5"),
    "hostname": os.environ.get("tg_proxy_host", "127.0.0.1"),
    "port": int(os.environ.get("tg_proxy_port", "1088")),
}

TG_CLIENT_KWARGS = {"proxy": TG_PROXY} if USE_PROXY else {}

TG_PROXY_URL = f"{TG_PROXY['scheme']}://{TG_PROXY['hostname']}:{TG_PROXY['port']}"