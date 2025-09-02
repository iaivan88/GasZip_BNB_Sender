import os
import yaml

from pathlib import Path
from typing import Dict, List, Generator, Union, Optional

from loguru import logger
from better_proxy import Proxy

from models import Config
from sys import exit


class ConfigurationError(Exception):
    pass


class ConfigLoader:
    REQUIRED_PARAMS = frozenset(
        {
            "attempts_and_delay_settings",
            "web3_settings"
        }
    )

    def __init__(self, base_path: Union[str, Path] = None):
        self.base_path = Path(base_path or os.getcwd())
        self.config_path = self.base_path / "config"
        self.data_path = self.config_path / "data"
        self.settings_path = self.config_path / "settings.yaml"

    @staticmethod
    def _read_file(file_path: Path, allow_empty: bool = False, is_yaml: bool = False) -> Union[List[str], Dict]:
        if not file_path.exists():
            raise ConfigurationError(f"File not found: {file_path}")

        try:
            if is_yaml:
                return yaml.safe_load(file_path.read_text(encoding='utf-8'))

            content = file_path.read_text(encoding='utf-8').strip()
            if not allow_empty and not content:
                raise ConfigurationError(f"File is empty: {file_path}")

            return [line.strip() for line in content.splitlines() if line.strip()]

        except Exception as e:
            raise ConfigurationError(f"Failed to read file {file_path}: {str(e)}")

    def _load_yaml(self) -> Dict:
        try:
            config = self._read_file(self.settings_path, is_yaml=True)
            missing_fields = self.REQUIRED_PARAMS - set(config.keys())

            if missing_fields:
                raise ConfigurationError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
            return config

        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML format: {e}")

    def _parse_proxies(self) -> Optional[List[str]]:
        try:
            proxy_lines = self._read_file(
                self.data_path / "proxies.txt", allow_empty=True
            )
            
            if not proxy_lines:
                logger.warning("No proxies found in proxies.txt - running without proxies")
                return []
                
            for proxy in proxy_lines:
                Proxy.from_str(proxy)

            return [Proxy.from_str(proxy).as_url for proxy in proxy_lines]
        except Exception as e:
            raise ConfigurationError(f"Failed to parse proxies: {e}")

    def _parse_accounts(
            self,
            filename: str,
    ) -> Generator[str, None, None]:
        try:
            lines = self._read_file(self.data_path / filename, allow_empty=False)

            for line in lines:
                try:
                    line = line.strip()
                    if not line:
                        continue

                    yield line

                except (ValueError, IndexError) as e:
                    logger.warning(f"Invalid account format: {line} | File: {filename} | Error: {e}")
                    exit(1)

        except ConfigurationError:
            raise

        except Exception as e:
            raise ConfigurationError(f"Failed to process accounts file: {str(e)} | File: {filename}")

    def _parse_wallets(self) -> List[str]:
        """Parse wallet private keys from wallets.txt file"""
        try:
            wallet_lines = self._read_file(
                self.data_path / "wallets.txt", allow_empty=False
            )
            
            wallets = []
            for i, line in enumerate(wallet_lines):
                try:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Remove 0x prefix if present
                    if line.startswith('0x'):
                        line = line[2:]
                    
                    # Validate private key length (64 hex characters)
                    if len(line) != 64:
                        logger.warning(f"Invalid private key length at line {i+1}: {line[:10]}... (expected 64 characters)")
                        continue
                    
                    # Validate hex format
                    try:
                        int(line, 16)
                    except ValueError:
                        logger.warning(f"Invalid hex format at line {i+1}: {line[:10]}...")
                        continue
                    
                    wallets.append(line)
                    
                except Exception as e:
                    logger.warning(f"Invalid wallet format at line {i+1}: {line} | Error: {e}")
                    continue
            
            if not wallets:
                raise ConfigurationError(
                    "No valid wallet private keys found in wallets.txt. "
                    "Please add at least one private key to proceed. "
                    "Each private key should be 64 hex characters (with or without 0x prefix)."
                )
                
            return wallets
            
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Failed to process wallets file: {str(e)}")

    def load(self) -> Config | None:
        try:
            params = self._load_yaml()
            proxies = self._parse_proxies()
            target_addresses = list(self._parse_accounts("target_addresses.txt"))
            if not target_addresses:
                logger.warning("No target addresses found in target_addresses.txt - this is fine for BNB bridging")
            wallet_private_keys = self._parse_wallets()

            # Validate wallet configuration
            if len(wallet_private_keys) < 1:
                raise ConfigurationError(
                    "Configuration error: You need at least one wallet private key in wallets.txt"
                )

            return Config(
                **params,
                target_addresses=target_addresses,
                wallet_private_keys=wallet_private_keys,
                proxies=proxies,
            )

        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            exit(1)


def load_config() -> Config:
    return ConfigLoader().load()
