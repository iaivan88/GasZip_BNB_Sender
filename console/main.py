import os
import sys
import time

import inquirer
from art import text2art
from colorama import Fore, Style
from inquirer.themes import GreenPassion

from loader import config
from sys import exit

from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text


sys.path.append(os.path.realpath("."))


class Console:
    MODULES = (
        "🔑 Launch sender",
        "❌ Exit",
    )
    MODULES_DATA = {
        "🔑 Launch sender": "launch_sender",
        "❌ Exit": "exit",
    }

    def __init__(self):
        self.rich_console = RichConsole()

    def show_dev_info(self):
        os.system("cls" if os.name == "nt" else "clear")
        self.show_loading_animation()

        title = text2art("JamBit", font="small")
        styled_title = Text(title, style="bold cyan")

        version = Text("VERSION: 1.0.0", style="blue")
        telegram = Text("Channel: https://t.me/JamBitPY", style="green")
        github = Text("GitHub: https://github.com/Jaammerr", style="green")

        dev_panel = Panel(
            Text.assemble(styled_title, "\n", version, "\n", telegram, "\n", github),
            border_style="yellow",
            expand=False,
            title="[bold green]Welcome[/bold green]",
            subtitle="[italic]Powered by Jammer[/italic]",
        )

        self.rich_console.print(dev_panel)
        print()

    def show_loading_animation(self):
        with self.rich_console.status("[bold green]Loading...", spinner="dots"):
            time.sleep(1.5)

    @staticmethod
    def prompt(data: list):
        answers = inquirer.prompt(data, theme=GreenPassion())
        return answers

    def get_module(self):
        questions = [
            inquirer.List(
                "module",
                message=Fore.LIGHTBLACK_EX + "Select the module" + Style.RESET_ALL,
                choices=self.MODULES,
            ),
        ]

        answers = self.prompt(questions)
        return answers.get("module")

    async def display_info(self):
        main_table = Table(title="Configuration Overview", box=box.ROUNDED, show_lines=True)

        accounts_table = Table(box=box.SIMPLE)
        accounts_table.add_column("Parameter", style="cyan")
        accounts_table.add_column("Value", style="magenta")

        accounts_table.add_row("Wallets configured", str(len(config.wallet_private_keys)))
        accounts_table.add_row("Proxies", str(len(config.proxies)))
        accounts_table.add_row("Operation", "BNB → opBNB Bridge")

        # Check configuration status
        if len(config.wallet_private_keys) == 0:
            accounts_table.add_row("⚠️  No wallets", "Add private keys to wallets.txt")
            self.rich_console.print(f"[bold red]⚠️  ERROR:[/bold red] No wallet private keys found in wallets.txt")
        else:
            accounts_table.add_row("✅ Configuration", f"{len(config.wallet_private_keys)} wallets will bridge BNB")
            self.rich_console.print(f"[bold green]✅[/bold green] Configuration is correct: {len(config.wallet_private_keys)} wallets will bridge BNB tokens to opBNB")

        main_table.add_column("Section")
        main_table.add_row("[bold]Files Information[/bold]", accounts_table)

        panel = Panel(
            main_table,
            expand=False,
            border_style="green",
            title="[bold yellow]System Information[/bold yellow]",
            subtitle="[italic]Use number keys to choose module[/italic]",
        )
        self.rich_console.print(panel)

    async def build(self) -> str | None:
        try:
            self.show_dev_info()
            await self.display_info()

            module = self.get_module()
            config.module = self.MODULES_DATA[module]

            if config.module == "exit":
                with self.rich_console.status(
                        "[bold red]Shutting down...", spinner="dots"
                ):
                    time.sleep(1)
                self.rich_console.print("[bold red]Goodbye! 👋[/bold red]")
                exit(0)

            return config.module

        except KeyboardInterrupt:
            self.rich_console.print(
                "\n[bold red]Interrupted by user. Exiting...[/bold red]"
            )
            exit(0)
