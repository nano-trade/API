import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup

# Exchange configurations
EXCHANGES = {
    "nano_banano": {
        "name": "Nano ↔ Banano",
        "api_url": "https://banano.nano.trade",
        "main_coin": "Nano",
        "main_symbol": "NANO",
        "coin": "Banano",
        "coin_symbol": "BAN",
        "main_explorer": "https://blocklattice.io/account",
        "coin_explorer": "https://creeper.banano.cc/account",
        "main_validator": lambda addr: len(addr) >= 65 and addr.startswith("nano_"),
        "coin_validator": lambda addr: len(addr) >= 64 and addr.startswith("ban_"),
        "price_invert": True,  # Invert price to show BAN per NANO
    },
    "solana_banano": {
        "name": "Solana ↔ Banano",
        "api_url": "https://solana.banano.trade",
        "main_coin": "Banano",
        "main_symbol": "BAN",
        "coin": "Solana",
        "coin_symbol": "SOL",
        "main_explorer": "https://creeper.banano.cc/account",
        "coin_explorer": "https://solana.fm/address",
        "main_validator": lambda addr: len(addr) >= 64 and addr.startswith("ban_"),
        "coin_validator": lambda addr: bool(re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", addr)),
        "price_invert": False,  # Price is BAN per SOL directly
    },
    "usdt_banano": {
        "name": "USDT ↔ Banano (Polygon)",
        "api_url": "https://usdt.banano.trade",
        "main_coin": "Banano",
        "main_symbol": "BAN",
        "coin": "USDT",
        "coin_symbol": "USDT",
        "main_explorer": "https://creeper.banano.cc/account",
        "coin_explorer": "https://polygonscan.com/address",
        "main_validator": lambda addr: len(addr) >= 64 and addr.startswith("ban_"),
        "coin_validator": lambda addr: bool(re.match(r"^0x[a-fA-F0-9]{40}$", addr)),
        "price_invert": False,  # Price is BAN per USDT directly
    },
}

SEPARATOR = "-" * 102


def validate_address(address: str, validator) -> bool:
    """Validate a cryptocurrency address using the provided validator."""
    return validator(address)


def get_addresses(currency: str, validator) -> list[str]:
    """Prompt user for addresses and validate them."""
    print(f"\nMultiple addresses supported, separated by space")

    while True:
        raw_input = input(f"Enter receive/refund {currency} address: ")
        addresses = raw_input.split()

        if not addresses:
            print(f"Please enter at least one {currency} address.")
            continue

        all_valid = all(validate_address(addr, validator) for addr in addresses)

        if not all_valid:
            print(f"Sorry, one or more addresses are not valid {currency} addresses.")
            continue

        print(f"List of {currency} addresses: {addresses}")
        return addresses


async def fetch_price(session: aiohttp.ClientSession, api_url: str) -> dict:
    """Fetch current buy/sell prices from the API."""
    async with session.get(f"{api_url}/api") as response:
        return await response.json()


async def process_trade(
    session: aiohttp.ClientSession,
    exchange: dict,
    main_address: str,
    coin_address: str,
    number: int,
    selection: str
) -> None:
    """Process a trade request and display the result."""
    api_url = exchange["api_url"]

    if selection == "buy":
        # Buying coin with main (e.g., buy BAN with NANO, or buy SOL with BAN)
        url = f"{api_url}/buy"
        data = {"coin_address_block": coin_address, "main_refund_address": main_address}
        receive_label = f"{exchange['coin']} receive address"
        refund_label = f"{exchange['main_coin']} refund address"
        receive_addr = coin_address
        refund_addr = main_address
        explorer_url = f"{exchange['coin_explorer']}/{coin_address}"
    else:
        # Selling coin for main (e.g., sell BAN for NANO, or sell SOL for BAN)
        url = f"{api_url}/sell"
        data = {"address_block": main_address, "coin_refund_address": coin_address}
        receive_label = f"{exchange['main_coin']} receive address"
        refund_label = f"{exchange['coin']} refund address"
        receive_addr = main_address
        refund_addr = coin_address
        explorer_url = f"{exchange['main_explorer']}/{main_address}"

    try:
        async with session.post(url, data=data) as response:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")

            if 'id="address' not in content:
                print("\nServer error or incorrect address, try again!")
                return

            deposit_address = soup.find("input")["value"]

            print(f"\nNumber {number}")
            print(SEPARATOR)
            print(f"{receive_label}: {receive_addr}")
            print(f"{refund_label}: {refund_addr}")
            print(f"DEPOSIT ADDRESS: {deposit_address}")
            print(SEPARATOR)
            print(f"Result: {explorer_url}\n")

    except aiohttp.ClientError as e:
        print(f"\nNetwork error: {e}")
    except Exception as e:
        print(f"\nError processing trade: {e}")


async def run_exchange(exchange_key: str) -> None:
    """Run the trading flow for a specific exchange."""
    exchange = EXCHANGES[exchange_key]

    options = [f"Buy {exchange['coin']}", f"Sell {exchange['coin']}"]

    input_message = "Pick an option:\n"
    for index, item in enumerate(options, 1):
        input_message += f"{index}) {item}\n"
    input_message += "Your choice: "

    user_input = ""
    while user_input not in ["1", "2"]:
        user_input = input(input_message)

    print(f"You picked: {options[int(user_input) - 1]}")

    async with aiohttp.ClientSession() as session:
        # Fetch and display prices
        try:
            price_data = await fetch_price(session, exchange["api_url"])

            # Display prices based on exchange configuration
            if exchange.get("price_invert", False):
                # Nano/Banano: invert to show BAN per NANO
                buy_rate = round(1 / price_data["user_buy_price"], 2)
                sell_rate = round(1 / price_data["user_sell_price"], 2)
                print(f"\nBuy Price: 1 {exchange['main_symbol']}:{buy_rate} {exchange['coin_symbol']} - Max Buy: {price_data['max_buy']:,} {exchange['main_symbol']}")
                print(f"Sell Price: {sell_rate} {exchange['coin_symbol']}:1 {exchange['main_symbol']} - Max Sell: {price_data['max_sell']:,} {exchange['coin_symbol']}")
            else:
                # Solana/Banano and USDT/Banano show rate directly
                buy_rate = float(price_data["user_buy_price"])
                sell_rate = float(price_data["user_sell_price"])
                max_sell_fmt = f"{price_data['max_sell']:.4f}" if price_data['max_sell'] < 100 else f"{price_data['max_sell']:,.2f}"
                print(f"\nBuy Price: 1 {exchange['coin_symbol']} = {buy_rate:,.2f} {exchange['main_symbol']} - Max Buy: {price_data['max_buy']:,} {exchange['main_symbol']}")
                print(f"Sell Price: 1 {exchange['coin_symbol']} = {sell_rate:,.2f} {exchange['main_symbol']} - Max Sell: {max_sell_fmt} {exchange['coin_symbol']}")

        except Exception as e:
            print(f"\nFailed to fetch prices: {e}")
            return

        # Get addresses from user
        main_addresses = get_addresses(exchange["main_coin"], exchange["main_validator"])
        coin_addresses = get_addresses(exchange["coin"], exchange["coin_validator"])

        if len(main_addresses) != len(coin_addresses):
            print(f"Error! {exchange['main_coin']} and {exchange['coin']} address lists must have the same length!")
            return

        # Process trades
        selection = "buy" if user_input == "1" else "sell"

        for i, (main_addr, coin_addr) in enumerate(zip(main_addresses, coin_addresses), 1):
            await process_trade(session, exchange, main_addr, coin_addr, i, selection)


async def main() -> None:
    """Main entry point - select exchange first."""
    print("Select Exchange:")
    print("1) Nano ↔ Banano (banano.nano.trade)")
    print("2) Solana ↔ Banano (solana.banano.trade)")
    print("3) USDT ↔ Banano (usdt.banano.trade) [Polygon]")

    exchange_choice = ""
    while exchange_choice not in ["1", "2", "3"]:
        exchange_choice = input("Your choice: ")

    exchange_keys = {"1": "nano_banano", "2": "solana_banano", "3": "usdt_banano"}
    exchange_key = exchange_keys[exchange_choice]
    print(f"\nUsing {EXCHANGES[exchange_key]['name']} exchange\n")

    await run_exchange(exchange_key)


if __name__ == "__main__":
    asyncio.run(main())
