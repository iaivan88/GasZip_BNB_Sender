import httpx
import asyncio

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

    async def test_gaszip_connection(self) -> bool:
        """Test if GasZip API is accessible and responding"""
        try:
            async with AsyncClient(proxy=self.proxy, timeout=10) as client:
                # Test with a simple endpoint first
                test_url = "https://backend.gas.zip/v2/quotes/56/1000000000000000/204"
                response = await client.get(test_url, params={'from': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', 'to': ''})
                
                logger.info(f"GasZip API test response: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"GasZip API test data: {data}")
                    return True
                else:
                    logger.error(f"GasZip API test failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"GasZip API connection test failed: {e}")
            return False

    async def create_quote(self, value: int) -> str:
        for attempt in range(3):
            try:
                async with AsyncClient(proxy=self.proxy, timeout=15) as client:
                    # For BNB bridging to opBNB, we need to specify the destination chain (204 = opBNB)
                    # The 'to' parameter should be empty or the user's opBNB address if they want to bridge to a specific address
                    params = {
                        'from': self.wallet_address,
                        'to': '',  # Empty for self-bridging to opBNB
                    }

                    # Try different API endpoints - GasZip might have changed their API structure
                    api_endpoints = [
                        f'https://backend.gas.zip/v2/quotes/56/{value}/204',  # Original endpoint
                        f'https://backend.gas.zip/v2/quotes/bsc/{value}/opbnb',  # Alternative with chain names
                        f'https://backend.gas.zip/v2/quotes/bsc/{value}/204',  # Mixed format
                        f'https://backend.gas.zip/api/v2/quotes/56/{value}/204',  # Alternative API path
                    ]
                    
                    last_error = None
                    
                    for endpoint in api_endpoints:
                        try:
                            logger.debug(f"Trying GasZip API endpoint: {endpoint}")
                            logger.debug(f"Parameters: {params}")
                            
                            response = await client.get(endpoint, params=params)
                            
                            if response.status_code == 200:
                                data = response.json()
                                logger.debug(f"GasZip API response: {data}")
                                
                                # Check for API errors first
                                if 'error' in data:
                                    last_error = f"GasZip API error: {data['error']}"
                                    continue
                                
                                if 'message' in data and 'error' in data.get('message', '').lower():
                                    last_error = f"GasZip API error: {data['message']}"
                                    continue
                                
                                # Look for calldata in the response
                                call_data = data.get('calldata')
                                if not call_data:
                                    # Try alternative field names
                                    call_data = data.get('callData') or data.get('data') or data.get('tx_data')
                                    
                                if call_data:
                                    logger.info(f"Successfully got quote from endpoint: {endpoint}")
                                    return call_data
                                else:
                                    last_error = f"Response missing calldata: {data}"
                                    continue
                                    
                            else:
                                last_error = f"HTTP {response.status_code}: {response.text}"
                                continue
                                
                        except Exception as e:
                            last_error = f"Endpoint {endpoint} failed: {e}"
                            continue
                    
                    # If we get here, all endpoints failed
                    raise Exception(f"All GasZip API endpoints failed. Last error: {last_error}")

            except (httpx.ReadTimeout, httpx.TimeoutException):
                logger.warning(f"Wallet: {self.wallet_address} | Attempt {attempt + 1}/3: Timeout while creating quote, retrying...")
                if attempt < 2:  # Don't sleep on the last attempt
                    await asyncio.sleep(2)
                continue

            except httpx.HTTPStatusError as e:
                logger.error(f"Wallet: {self.wallet_address} | HTTP error {e.response.status_code}: {e.response.text}")
                if attempt < 2:
                    await asyncio.sleep(2)
                continue
                
            except Exception as e:
                logger.error(f"Wallet: {self.wallet_address} | Attempt {attempt + 1}/3: Error while creating quote: {e}")
                if attempt < 2:
                    await asyncio.sleep(2)
                continue
        
        # If we get here, all attempts failed
        raise Exception("Failed to create quote after 3 attempts")

    async def _build_trx(self, amount: float) -> TxParams:
        try:
            value = int(self.to_wei(amount, "ether"))
            logger.debug(f"Building transaction for {amount} BNB ({value} wei)")
            
            call_data = await self.create_quote(value)
            logger.debug(f"Got calldata: {call_data[:50]}...")
            
            gas_price = await self.eth.gas_price
            logger.debug(f"Gas price: {gas_price}")
            
            # Estimate gas for the transaction
            gas_estimate_params = {
                "from": self.wallet_address,
                "to": self.to_checksum_address(self.BASE_TARGET),
                "value": self.to_wei(amount, "ether"),
                "data": HexStr(call_data),
            }
            logger.debug(f"Estimating gas with params: {gas_estimate_params}")
            
            gas_limit = await self.eth.estimate_gas(gas_estimate_params)
            logger.debug(f"Estimated gas limit: {gas_limit}")
            
            transaction = {
                "chainId": await self.eth.chain_id,
                "data": HexStr(call_data),
                "from": self.wallet_address,
                "to": self.to_checksum_address(self.BASE_TARGET),
                "value": self.to_wei(amount, "ether"),
                "gasPrice": gas_price,
                "nonce": await self.transactions_count(),
                "gas": gas_limit,
            }
            
            logger.debug(f"Built transaction: {transaction}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error building transaction: {e}")
            raise

    async def process_bridge(self, amount: float) -> tuple[bool, str]:
        try:
            # Test GasZip API connection first
            logger.info(f"Testing GasZip API connection for wallet {self.wallet_address}")
            if not await self.test_gaszip_connection():
                return False, "GasZip API is not accessible"
            
            transaction = await self._build_trx(amount)
            await self.check_trx_availability(transaction)
            return await self._process_transaction(transaction)

        except Exception as error:
            return False, str(error)
