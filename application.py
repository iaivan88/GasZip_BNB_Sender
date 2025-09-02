from loader import config
from utils import Progress

from console import Console
from core.bot.base import Bot
from loader import file_operations


class ApplicationManager:

    @staticmethod
    async def run() -> None:
        await file_operations.setup_files()

        while True:
            await Console().build()

            if config.module == "launch_sender":
                await Bot().process_bridges()

            input("\nPress Enter to continue...")
