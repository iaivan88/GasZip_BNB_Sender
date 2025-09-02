from dataclasses import dataclass
from pydantic import BaseModel, PositiveInt, ConfigDict, Field, PositiveFloat

from core.web3.wallet import Web3Wallet


class BaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)



@dataclass
class Range:
    min: int
    max: int


@dataclass
class PositiveFloatRange:
    min: PositiveFloat
    max: PositiveFloat


@dataclass
class PositiveIntRange:
    min: PositiveInt
    max: PositiveInt


@dataclass
class AttemptsAndDelaySettings:
    delay_before_start: Range



@dataclass
class Web3Settings:
    wallet_private_keys: list[str]  # List of private keys for different wallets
    bsc_rpc_url: str

    amount_to_bridge: PositiveFloatRange




class Config(BaseConfig):
    target_addresses: list[str] = Field(default_factory=list)
    wallet_private_keys: list[str] = Field(default_factory=list)  # Loaded from wallets.txt
    proxies: list[str] = Field(default_factory=list)

    web3_settings: Web3Settings
    attempts_and_delay_settings: AttemptsAndDelaySettings

    module: str = ""
