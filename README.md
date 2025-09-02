# 🌐 BNB > opBNB Sender via GasZip [v1.0]

<div align="center">
  
  <p align="center">
    <a href="https://t.me/JamBitPY">
      <img src="https://img.shields.io/badge/Telegram-Channel-blue?style=for-the-badge&logo=telegram" alt="Telegram Channel">
    </a>
    <a href="https://t.me/JamBitChat">
      <img src="https://img.shields.io/badge/Telegram-Chat-blue?style=for-the-badge&logo=telegram" alt="Telegram Chat">
    </a>
  </p>

</div>


## 🛠️ Installation

1. **Clone the Repository**
   ```bash
   git clone [repository URL]
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   source venv/bin/activate      # Unix/MacOS
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📝 Input Files Structure

### 📁data/wallets.txt

```plaintext
# Add your wallet private keys here (one per line)
# Each wallet will bridge BNB tokens to opBNB
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
0x567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234
```

### 📁 data/proxies.txt
```
http://user:pass@ip:port
http://ip:port:user:pass
http://user:pass:ip:port
```

## 🔑 Multiple Wallet BNB Bridging

### ⚠️ Important: Each Wallet Bridges BNB

The system now supports bridging BNB tokens from multiple wallets to opBNB:

- **Wallet 1** → **Bridge BNB to opBNB**
- **Wallet 2** → **Bridge BNB to opBNB**
- **Wallet 3** → **Bridge BNB to opBNB**
- And so on...

### 📋 Configuration Requirements

1. **Wallet Private Keys**: Multiple private keys in `wallets.txt` (one per line)
2. **Balance Check**: Ensure each wallet has sufficient BNB for gas fees and the amount to bridge
3. **File Structure**: Private keys are loaded from `config/data/wallets.txt`
4. **Target Addresses**: Not needed - each wallet bridges its own BNB

### 🔧 Settings.yaml Example

```yaml
web3_settings:
  bsc_rpc_url: "https://bsc.drpc.org"
  # Private keys are loaded from wallets.txt file
  
  amount_to_bridge:
    min: 0.000048554
    max: 0.00006
```

### ⚡ Benefits of Multiple Wallets

- **Distributed Risk**: No single wallet handles all transactions
- **Better Success Rate**: Multiple wallets can operate simultaneously
- **Easier Tracking**: Each transaction is clearly associated with a specific wallet
- **Compliance**: Useful for managing multiple accounts or projects
- **Individual Bridging**: Each wallet bridges its own BNB tokens

## 📊 Results

```plaintext
📁 results/sender/
  ├── 📄 bridge_success.txt  # Successful bridge wallet addresses
  ├── 📄 bridge_failed.txt  # Failed bridge wallet addresses
  ```

## 🚀 Usage


1. Configure your settings in settings.yaml
2. Add your accounts to target_addresses.txt
3. Add proxies to proxies.txt
4. Run the checker:
   ```bash
   python run.py
   ```
