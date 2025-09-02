import asyncio

from utils import load_config, FileOperations, ProxyManager

config = load_config()
file_operations = FileOperations()
semaphore = asyncio.Semaphore(1)

proxy_manager = ProxyManager(check_uniqueness=True)
proxy_manager.load_proxy(proxies=config.proxies)
