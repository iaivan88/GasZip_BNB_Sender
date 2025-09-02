import asyncio
import random

from loguru import logger
from loader import config, semaphore, proxy_manager, file_operations
from core.web3.modules.sender import SenderModule



class Bot:

    @staticmethod
    async def safe_bridge(
            delay: int,
            private_key: str,
            rpc_url: str,
            target_address: str,
            amount: float,
            proxy: str,
            wallet_index: int = None
    ):
        sender = None

        async with semaphore:
            try:
                if delay > 0:
                    logger.info(f"Wallet {wallet_index} | Waiting for {delay} seconds before starting..")
                    await asyncio.sleep(delay)

                logger.info(f"Wallet {wallet_index} | Bridging {amount:.8f} BNB to opBNB..")
                sender = SenderModule(
                    private_key=private_key,
                    target_address="",  # Not used for bridging
                    rpc_url=rpc_url,
                    proxy=proxy
                )
                status, result = await sender.process_bridge(amount)

                if status:
                    tx = f"https://bscscan.com/tx/0x{result}" if not result.startswith("0x") else f"https://bscscan.com/tx/{result}"
                    logger.success(f"Wallet {wallet_index} | Successfully bridged {amount:.8f} BNB to opBNB | TX: {tx}")
                else:
                    logger.error(f"Wallet {wallet_index} | Failed to bridge {amount:.8f} BNB to opBNB | Error: {result}")

                await file_operations.export_result(f"Wallet_{wallet_index}", status, "sender")

            finally:
                if sender:
                    await sender.cleanup()


    async def process_bridges(self):
        tasks = []

        logger.info(f"Preparing BNB bridge tasks for {len(config.wallet_private_keys)} wallets")
        
        for i, private_key in enumerate(config.wallet_private_keys):
            amount_to_bridge = round(random.uniform(config.web3_settings.amount_to_bridge.min, config.web3_settings.amount_to_bridge.max), 8)
            proxy = await proxy_manager.get_proxy()
            delay = random.randint(
                config.attempts_and_delay_settings.delay_before_start.min,
                config.attempts_and_delay_settings.delay_before_start.max
            ) if config.attempts_and_delay_settings.delay_before_start.max > 0 else 0

            tasks.append(
                asyncio.create_task(
                    self.safe_bridge(
                        delay=delay,
                        private_key=private_key,
                        rpc_url=config.web3_settings.bsc_rpc_url,
                        target_address="",  # Not used for bridging
                        amount=amount_to_bridge,
                        proxy=proxy.as_url,
                        wallet_index=i + 1
                    )
                )
            )

        logger.success(f"Prepared {len(tasks)} BNB bridge tasks for {len(config.wallet_private_keys)} wallets. Starting execution..")
        await asyncio.gather(*tasks)
