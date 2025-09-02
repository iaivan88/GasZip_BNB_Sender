from eth_account import Account
from eth_typing import ChecksumAddress

from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.types import Nonce, TxParams

from typing import Any
from loguru import logger





class Web3Wallet(AsyncWeb3, Account):
    def __init__(self, private_key: str, rpc_url: str = None, proxy: str = None):
        self.web3_provider = AsyncHTTPProvider(
            endpoint_uri=rpc_url,
            request_kwargs={
                "proxy": proxy if proxy else None,
                "ssl": False
            }
        )

        super().__init__(provider=self.web3_provider, modules={"eth": (AsyncEth,)})
        self.keypair = self.from_key(private_key)

    @property
    def wallet_address(self):
        return self.keypair.address

    @staticmethod
    def _get_checksum_address(address: str) -> ChecksumAddress:
        return AsyncWeb3.to_checksum_address(address)

    async def transactions_count(self) -> Nonce:
        return await self.eth.get_transaction_count(self.keypair.address)

    async def check_balance(self) -> None:
        balance = await self.eth.get_balance(self.keypair.address)

        if balance <= 0:
            raise Exception(f"ETH balance is empty")

    async def human_balance(self) -> float:
        balance = await self.eth.get_balance(self.keypair.address)
        return float(AsyncWeb3.from_wei(balance, "ether"))

    async def _build_base_transaction(self, contract_function) -> TxParams:
        gas_estimate = await contract_function.estimate_gas({"from": self.keypair.address})

        return {
            "gasPrice": await self.eth.gas_price,
            "nonce": await self.transactions_count(),
            "gas": int(gas_estimate * 1.2),
        }

    async def check_trx_availability(self, transaction: TxParams) -> None:
        balance = await self.human_balance()
        required = float(self.from_wei(int(transaction.get('value', 0)), "ether"))

        if balance < required:
            raise Exception(f"BNB balance is not enough. Required: {required} BNB | Available: {balance} BNB")

    async def _process_transaction(self, transaction: Any) -> tuple[bool, str]:
        try:
            status, result = await self.send_and_verify_transaction(transaction)
            return status, result

        except Exception as error:
            return False, str(error)


    async def send_and_verify_transaction(self, trx: Any) -> tuple[bool | Any, str]:
        signed = self.keypair.sign_transaction(trx)
        tx_hash = await self.eth.send_raw_transaction(signed.raw_transaction)
        receipt = await self.eth.wait_for_transaction_receipt(tx_hash)
        return receipt["status"] == 1, tx_hash.hex()

    async def cleanup(self):
        try:
            if hasattr(self.web3_provider, "disconnect"):
                await self.web3_provider.disconnect()

            if hasattr(self.web3_provider, "_request_kwargs") and isinstance(
                self.web3_provider._request_kwargs, dict
            ):
                session = self.web3_provider._request_kwargs.get("session")
                if session and hasattr(session, "close") and not session.closed:
                    await session.close()

        except Exception as e:
            logger.warning(f"Account: {self.wallet_address} | Cannot cleanup Web3 provider: {e}")
