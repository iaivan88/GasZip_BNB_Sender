import httpx

from eth_typing import HexStr
from loguru import logger
from web3.types import TxParams

from core.web3.wallet import Web3Wallet
from httpx import AsyncClient


class SenderModule(Web3Wallet):
    BASE_TARGET = "0x391E7C679d29bD940d63be94AD22A25d25b5A604"

    def __init__(self, private_key: str, target_address: str, rpc_url: str, proxy: str = None):
        super().__init__(private_key, rpc_url, proxy)
        self.proxy = proxy
        self.target_address = target_address

    async def create_quote(self, value: int) -> str:
        for _ in range(3):
            try:
                async with AsyncClient(proxy=self.proxy, timeout=10) as client:
                    params = {
                        'from': self.wallet_address,
                        'to': self.target_address,
                    }

                    response = await client.get(f'https://backend.gas.zip/v2/quotes/56/{value}/204', params=params)
                    response.raise_for_status()

                    data = response.json()
                    call_data = data.get('calldata')
                    if not call_data:
                        raise Exception("Failed to get quote data")

                    return call_data

            except (httpx.ReadTimeout, httpx.TimeoutException):
                logger.error(f"Target: {self.target_address} | Timeout while creating quote, retrying...")
                continue

            except Exception as e:
                raise Exception(f"Error while creating quote: {e}")


    async def _build_trx(self, amount: float) -> TxParams:
        value = int(self.to_wei(amount, "ether"))
        call_data = await self.create_quote(value)

        gas_price = await self.eth.gas_price
        gas_limit = await self.eth.estimate_gas({
            "from": self.wallet_address,
            "to": self.to_checksum_address(self.BASE_TARGET),
            "value": self.to_wei(amount, "ether"),
            "data": HexStr(call_data),
        })

        return {
            "chainId": await self.eth.chain_id,
            "data": HexStr(call_data),
            "from": self.wallet_address,
            "to": self.to_checksum_address(self.BASE_TARGET),
            "value": self.to_wei(amount, "ether"),
            "gasPrice": gas_price,
            "nonce": await self.transactions_count(),
            "gas": gas_limit,
        }

    async def process_bridge(self, amount: float) -> tuple[bool, str]:
        try:
            transaction = await self._build_trx(amount)
            await self.check_trx_availability(transaction)
            return await self._process_transaction(transaction)

        except Exception as error:
            logger.exception(error)
            return False, str(error)
