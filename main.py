from bs4 import BeautifulSoup
import aiohttp
import asyncio

NanoAddressList = [str(XNO) for XNO in input("Enter multiple Nano address, separated by space: ").split()]
print("List of XNO address: ", NanoAddressList)

BananoAddressList = [str(BAN) for BAN in input("Enter multiple Banano address, separated by space: ").split()]
print("List of address: ", BananoAddressList)

async def info():
    tasks = []
    for i in range(len(NanoAddressList)):
        Number = i+1
        NanoAddress = NanoAddressList[i]
        BananoAddress = BananoAddressList[i]
        data = {'address_block': NanoAddress, 'coin_refund_address': BananoAddress}
        await tracker(NanoAddress, BananoAddress, Number, data)

async def tracker(NanoAddress, BananoAddress, Number, data):
    async with aiohttp.ClientSession() as session:
        # use the session to make a POST request
        async with session.post("https://banano.nano.trade/sell", data=data, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36'}) as response:
            content = await response.text()
            source = BeautifulSoup(content, "html.parser")
            deposit_address = source.find('input')['value']
            print(f'Number {Number}')
            print('------------------------------------------------------------------------------------------------------')
            print(f'Nano receive address: {NanoAddress}')
            print(f'Banano refund address: {BananoAddress}')
            print(f'DEPOSIT ADDRESS: {deposit_address}')
            print('------------------------------------------------------------------------------------------------------')
            print(f'LINK: https://nanolooker.com/account/{NanoAddress}\n')

# run the info function to send all of the requests
if len(NanoAddressList) == len(BananoAddressList):
    print('\nStart Swapping Procedure\n')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(info())
else:
    print('Error! Nano Address and Banano Address need to be in the same length!')
