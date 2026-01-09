# Banano Trade CLI

A command-line tool for swapping cryptocurrencies using the Banano exchange services.

## Supported Exchanges

| Exchange | URL | Swap Pair |
|----------|-----|-----------|
| **Nano ↔ Banano** | [banano.nano.trade](https://banano.nano.trade) | NANO ↔ BAN |
| **Solana ↔ Banano** | [solana.banano.trade](https://solana.banano.trade) | SOL ↔ BAN |
| **USDT ↔ Banano** | [usdt.banano.trade](https://usdt.banano.trade) | USDT (Polygon) ↔ BAN |

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Run the script                                              │
│                    ↓                                            │
│  2. Select exchange (Nano/Solana/USDT ↔ Banano)                 │
│                    ↓                                            │
│  3. Choose: Buy or Sell                                         │
│                    ↓                                            │
│  4. See current exchange rates and limits                       │
│                    ↓                                            │
│  5. Enter your addresses for both currencies                    │
│                    ↓                                            │
│  6. Get a DEPOSIT ADDRESS from the exchange                     │
│                    ↓                                            │
│  7. Send your crypto to that deposit address                    │
│                    ↓                                            │
│  8. Receive swapped crypto at your address!                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Example Session

```
Select Exchange:
1) Nano ↔ Banano (banano.nano.trade)
2) Solana ↔ Banano (solana.banano.trade)
3) USDT ↔ Banano (usdt.banano.trade) [Polygon]
Your choice: 1

Using Nano ↔ Banano exchange

Pick an option:
1) Buy Banano
2) Sell Banano
Your choice: 1
You picked: Buy Banano

Buy Price: 1 NANO:85.5 BAN - Max Buy: 500 NANO
Sell Price: 82.3 BAN:1 NANO - Max Sell: 50,000 BAN

Multiple addresses supported, separated by space
Enter receive/refund Nano address: nano_1abc...xyz
List of Nano addresses: ['nano_1abc...xyz']

Multiple addresses supported, separated by space
Enter receive/refund Banano address: ban_1abc...xyz
List of Banano addresses: ['ban_1abc...xyz']

Number 1
------------------------------------------------------------------------------------------------------
Banano receive address: ban_1abc...xyz
Nano refund address: nano_1abc...xyz
DEPOSIT ADDRESS: nano_3deposit...address
------------------------------------------------------------------------------------------------------
Result: https://creeper.banano.cc/account/ban_1abc...xyz
```

## Understanding the Output

| Field | Description |
|-------|-------------|
| **Buy Price** | Exchange rate when buying the coin |
| **Sell Price** | Exchange rate when selling the coin |
| **Max Buy** | Maximum amount you can send in one buy trade |
| **Max Sell** | Maximum amount you can send in one sell trade |
| **DEPOSIT ADDRESS** | Send your crypto HERE to complete the swap |
| **Result** | Block explorer link to track your receiving address |

## Multiple Addresses

You can process multiple swaps at once by entering addresses separated by spaces:

```
Enter receive/refund Nano address: nano_addr1 nano_addr2 nano_addr3
Enter receive/refund Banano address: ban_addr1 ban_addr2 ban_addr3
```

This creates 3 separate trades, each pairing corresponding addresses.

## Installation & Usage

### Python

```bash
cd python

# Install dependencies
pip install aiohttp beautifulsoup4

# Run
python main.py
```

### JavaScript (Node.js 18+)

```bash
cd javascript

# No dependencies needed (uses built-in fetch)
node main.js
```

## Address Formats

| Currency | Format | Example |
|----------|--------|---------|
| Nano | `nano_` prefix, 65 chars | `nano_1a2b3c...` |
| Banano | `ban_` prefix, 64 chars | `ban_1a2b3c...` |
| Solana | Base58, 32-44 chars | `7xKXtg2CW87...` |
| USDT (Polygon) | `0x` prefix, 42 chars | `0x1a2b3c4d...` |

## Block Explorers

| Currency | Explorer |
|----------|----------|
| Nano | https://blocklattice.io/account/{address} |
| Banano | https://creeper.banano.cc/account/{address} |
| Solana | https://solana.fm/address/{address} |
| USDT (Polygon) | https://polygonscan.com/address/{address} |

## API Reference

All exchanges use the same API structure:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api` | GET | Get current exchange rates and limits |
| `/buy` | POST | Create a buy order |
| `/sell` | POST | Create a sell order |

### GET /api Response

```json
{
  "user_buy_price": 0.0117,
  "user_sell_price": 0.0122,
  "max_buy": 500,
  "max_sell": 50000
}
```

### POST /buy Parameters

| Parameter | Description |
|-----------|-------------|
| `coin_address_block` | Your receiving address for the coin you're buying |
| `main_refund_address` | Your refund address (in case trade fails) |

### POST /sell Parameters

| Parameter | Description |
|-----------|-------------|
| `address_block` | Your receiving address for what you're selling for |
| `coin_refund_address` | Your refund address (in case trade fails) |

## API URLs

| Exchange | Base URL |
|----------|----------|
| Nano ↔ Banano | `https://banano.nano.trade` |
| Solana ↔ Banano | `https://solana.banano.trade` |
| USDT ↔ Banano | `https://usdt.banano.trade` |

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| "Not a valid address" | Address format incorrect | Check the address format for that currency |
| "Server error" | API is down or address rejected | Try again later or verify addresses |
| "Address lists must have same length" | Mismatched number of addresses | Enter equal number of addresses for both currencies |

## License

MIT
