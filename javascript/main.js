const readline = require("readline");

// Exchange configurations
const EXCHANGES = {
    nano_banano: {
        name: "Nano ↔ Banano",
        apiUrl: "https://banano.nano.trade",
        mainCoin: "Nano",
        mainSymbol: "NANO",
        coin: "Banano",
        coinSymbol: "BAN",
        mainExplorer: "https://blocklattice.io/account",
        coinExplorer: "https://creeper.banano.cc/account",
        mainValidator: (addr) => addr.length >= 65 && addr.startsWith("nano_"),
        coinValidator: (addr) => addr.length >= 64 && addr.startsWith("ban_"),
        priceInvert: true,  // Invert price to show BAN per NANO
    },
    solana_banano: {
        name: "Solana ↔ Banano",
        apiUrl: "https://solana.banano.trade",
        mainCoin: "Banano",
        mainSymbol: "BAN",
        coin: "Solana",
        coinSymbol: "SOL",
        mainExplorer: "https://creeper.banano.cc/account",
        coinExplorer: "https://solana.fm/address",
        mainValidator: (addr) => addr.length >= 64 && addr.startsWith("ban_"),
        coinValidator: (addr) => /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(addr),
        priceInvert: false,  // Price is BAN per SOL directly
    },
    usdt_banano: {
        name: "USDT ↔ Banano (Polygon)",
        apiUrl: "https://usdt.banano.trade",
        mainCoin: "Banano",
        mainSymbol: "BAN",
        coin: "USDT",
        coinSymbol: "USDT",
        mainExplorer: "https://creeper.banano.cc/account",
        coinExplorer: "https://polygonscan.com/address",
        mainValidator: (addr) => addr.length >= 64 && addr.startsWith("ban_"),
        coinValidator: (addr) => /^0x[a-fA-F0-9]{40}$/.test(addr),
        priceInvert: false,  // Price is BAN per USDT directly
    },
};

const SEPARATOR = "-".repeat(102);

// Create readline interface for user input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const question = (prompt) => new Promise((resolve) => rl.question(prompt, resolve));

/**
 * Validate a cryptocurrency address using the provided validator
 */
function validateAddress(address, validator) {
    return validator(address);
}

/**
 * Prompt user for addresses and validate them
 */
async function getAddresses(currency, validator) {
    console.log(`\nMultiple addresses supported, separated by space`);

    while (true) {
        const rawInput = await question(`Enter receive/refund ${currency} address: `);
        const addresses = rawInput.trim().split(/\s+/).filter(Boolean);

        if (addresses.length === 0) {
            console.log(`Please enter at least one ${currency} address.`);
            continue;
        }

        const allValid = addresses.every(addr => validateAddress(addr, validator));

        if (!allValid) {
            console.log(`Sorry, one or more addresses are not valid ${currency} addresses.`);
            continue;
        }

        console.log(`List of ${currency} addresses:`, addresses);
        return addresses;
    }
}

/**
 * Fetch current buy/sell prices from the API
 */
async function fetchPrice(apiUrl) {
    const response = await fetch(`${apiUrl}/api`);
    return response.json();
}

/**
 * Process a trade request and display the result
 */
async function processTrade(exchange, mainAddress, coinAddress, number, selection) {
    const apiUrl = exchange.apiUrl;
    let url, data, receiveLabel, refundLabel, receiveAddr, refundAddr, explorerUrl;

    if (selection === "buy") {
        // Buying coin with main (e.g., buy BAN with NANO, or buy SOL with BAN)
        url = `${apiUrl}/buy`;
        data = { coin_address_block: coinAddress, main_refund_address: mainAddress };
        receiveLabel = `${exchange.coin} receive address`;
        refundLabel = `${exchange.mainCoin} refund address`;
        receiveAddr = coinAddress;
        refundAddr = mainAddress;
        explorerUrl = `${exchange.coinExplorer}/${coinAddress}`;
    } else {
        // Selling coin for main (e.g., sell BAN for NANO, or sell SOL for BAN)
        url = `${apiUrl}/sell`;
        data = { address_block: mainAddress, coin_refund_address: coinAddress };
        receiveLabel = `${exchange.mainCoin} receive address`;
        refundLabel = `${exchange.coin} refund address`;
        receiveAddr = mainAddress;
        refundAddr = coinAddress;
        explorerUrl = `${exchange.mainExplorer}/${mainAddress}`;
    }

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams(data)
        });

        const content = await response.text();

        if (!content.includes('id="address')) {
            console.log("\nServer error or incorrect address, try again!");
            return;
        }

        // Extract deposit address from response
        const match = content.match(/value="([^"]+)"/);
        if (!match) {
            console.log("\nCould not parse deposit address from response!");
            return;
        }

        const depositAddress = match[1];

        console.log(`\nNumber ${number}`);
        console.log(SEPARATOR);
        console.log(`${receiveLabel}: ${receiveAddr}`);
        console.log(`${refundLabel}: ${refundAddr}`);
        console.log(`DEPOSIT ADDRESS: ${depositAddress}`);
        console.log(SEPARATOR);
        console.log(`Result: ${explorerUrl}\n`);

    } catch (error) {
        console.log(`\nNetwork error: ${error.message}`);
    }
}

/**
 * Run the trading flow for a specific exchange
 */
async function runExchange(exchangeKey) {
    const exchange = EXCHANGES[exchangeKey];

    const options = [`Buy ${exchange.coin}`, `Sell ${exchange.coin}`];

    let inputMessage = "Pick an option:\n";
    options.forEach((item, index) => {
        inputMessage += `${index + 1}) ${item}\n`;
    });
    inputMessage += "Your choice: ";

    let userInput = "";
    while (!["1", "2"].includes(userInput)) {
        userInput = await question(inputMessage);
    }

    console.log(`You picked: ${options[parseInt(userInput) - 1]}`);

    // Fetch and display prices
    try {
        const priceData = await fetchPrice(exchange.apiUrl);

        // Display prices based on exchange configuration
        if (exchange.priceInvert) {
            // Nano/Banano: invert to show BAN per NANO
            const buyRate = (1 / priceData.user_buy_price).toFixed(2);
            const sellRate = (1 / priceData.user_sell_price).toFixed(2);
            console.log(`\nBuy Price: 1 ${exchange.mainSymbol}:${buyRate} ${exchange.coinSymbol} - Max Buy: ${priceData.max_buy.toLocaleString()} ${exchange.mainSymbol}`);
            console.log(`Sell Price: ${sellRate} ${exchange.coinSymbol}:1 ${exchange.mainSymbol} - Max Sell: ${priceData.max_sell.toLocaleString()} ${exchange.coinSymbol}`);
        } else {
            // Solana/Banano and USDT/Banano show rate directly
            const buyRate = parseFloat(priceData.user_buy_price).toFixed(2);
            const sellRate = parseFloat(priceData.user_sell_price).toFixed(2);
            const maxSellFmt = priceData.max_sell < 100 ? priceData.max_sell.toFixed(4) : priceData.max_sell.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
            console.log(`\nBuy Price: 1 ${exchange.coinSymbol} = ${Number(buyRate).toLocaleString()} ${exchange.mainSymbol} - Max Buy: ${priceData.max_buy.toLocaleString()} ${exchange.mainSymbol}`);
            console.log(`Sell Price: 1 ${exchange.coinSymbol} = ${Number(sellRate).toLocaleString()} ${exchange.mainSymbol} - Max Sell: ${maxSellFmt} ${exchange.coinSymbol}`);
        }
    } catch (error) {
        console.log(`\nFailed to fetch prices: ${error.message}`);
        return;
    }

    // Get addresses from user
    const mainAddresses = await getAddresses(exchange.mainCoin, exchange.mainValidator);
    const coinAddresses = await getAddresses(exchange.coin, exchange.coinValidator);

    if (mainAddresses.length !== coinAddresses.length) {
        console.log(`Error! ${exchange.mainCoin} and ${exchange.coin} address lists must have the same length!`);
        return;
    }

    // Process trades
    const selection = userInput === "1" ? "buy" : "sell";

    for (let i = 0; i < mainAddresses.length; i++) {
        await processTrade(exchange, mainAddresses[i], coinAddresses[i], i + 1, selection);
    }
}

/**
 * Main entry point - select exchange first
 */
async function main() {
    console.log("Select Exchange:");
    console.log("1) Nano ↔ Banano (banano.nano.trade)");
    console.log("2) Solana ↔ Banano (solana.banano.trade)");
    console.log("3) USDT ↔ Banano (usdt.banano.trade) [Polygon]");

    let exchangeChoice = "";
    while (!["1", "2", "3"].includes(exchangeChoice)) {
        exchangeChoice = await question("Your choice: ");
    }

    const exchangeKeys = { "1": "nano_banano", "2": "solana_banano", "3": "usdt_banano" };
    const exchangeKey = exchangeKeys[exchangeChoice];
    console.log(`\nUsing ${EXCHANGES[exchangeKey].name} exchange\n`);

    await runExchange(exchangeKey);

    rl.close();
}

main().catch(console.error);
