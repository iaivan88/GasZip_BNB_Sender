# GasZip BNB Sender

A Python application for bridging BNB tokens from Binance Smart Chain (BSC) to opBNB.

## Features

- Automated BNB bridging from BSC to opBNB
- Support for multiple wallet configurations
- Configurable bridge amounts with min/max ranges
- Proxy support for enhanced privacy
- Random delays between operations
- Comprehensive logging and error handling

## Prerequisites

- Python 3.8+
- BNB tokens on Binance Smart Chain
- Wallet private keys

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### 1. Wallet Configuration (`config/data/wallets.txt`)

Add your wallet private keys, one per line:

```
# Remove the 0x prefix if your private keys don't have it
1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
```

**⚠️ IMPORTANT**: 
- Each private key should be 64 hex characters
- Ensure each wallet has sufficient BNB for gas fees + bridge amount
- Keep your private keys secure and never share them

### 2. Application Settings (`config/settings.yaml`)

```yaml
web3_settings:
  bsc_rpc_url: "https://bsc.drpc.org"  # BSC RPC endpoint
  amount_to_bridge:
    min: 0.000048554  # Minimum BNB to bridge
    max: 0.00006      # Maximum BNB to bridge

attempts_and_delay_settings:
  delay_before_start:
    min: 2  # Minimum delay in seconds
    max: 3  # Maximum delay in seconds
```

### 3. Proxy Configuration (`config/data/proxies.txt`) - Optional

Add proxy configurations if needed:

```
http://username:password@proxy.example.com:8080
socks5://username:password@proxy.example.com:1080
```

Leave empty to run without proxies.

### 4. Target Addresses (`config/data/target_addresses.txt`) - Optional

For BNB bridging operations, leave this file empty. Each wallet bridges its own BNB.

## Usage

1. Configure your wallets and settings as described above
2. Run the application:
   ```bash
   python run.py
   ```

## How It Works

1. The application loads wallet configurations from `wallets.txt`
2. For each wallet, it calculates a random bridge amount within the configured range
3. It connects to BSC using the configured RPC endpoint
4. Each wallet bridges its BNB tokens to opBNB
5. Random delays are applied between operations

## Security Notes

- Never commit private keys to version control
- Use environment variables for sensitive data in production
- Consider using hardware wallets for large amounts
- Regularly rotate your private keys

## Troubleshooting

### Common Issues

1. **"No valid wallet private keys found"**
   - Ensure `wallets.txt` contains valid 64-character hex private keys
   - Remove any `0x` prefixes if present

2. **"Configuration loading failed"**
   - Check that all required fields are present in `settings.yaml`
   - Verify file permissions and paths

3. **"Insufficient BNB balance"**
   - Ensure each wallet has enough BNB for gas fees + bridge amount
   - Check current BNB balances on BSC

### Logs

The application uses structured logging with loguru. Check the console output for detailed information about operations and any errors.

## License

This project is for educational purposes. Use at your own risk.

## Disclaimer

This software is provided "as is" without warranty. Cryptocurrency transactions carry inherent risks. Always test with small amounts first and ensure you understand the implications of your actions.
