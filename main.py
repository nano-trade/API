import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio

# select method
async def select():
    options = ['Buy Banano', 'Sell Banano']
    user_input = ''
    input_message = "Pick an option:\n"
    for index, item in enumerate(options):
        input_message += f'{index+1}) {item}\n'
    input_message += 'Your choice: '
    while user_input not in map(str, range(1, len(options) + 1)):
        user_input = input(input_message)
    print(f'You picked: {options[int(user_input) - 1]}')
    getPrice=requests.get('https://banano.nano.trade/api').json()


    print('\nBuy Price: 1 NANO:' + str(round(1/getPrice['user_buy_price'],2)) + ' BANANO - Max Buy: ' + str(getPrice['max_buy']) + ' NANO')
    print('Sell Price: ' + str(round(1/getPrice['user_sell_price'],2)) + ' BANANO:1 NANO - Max Sell: ' + str(getPrice['max_sell']) + ' BANANO')

    # user defined list of single or multiple address
    print('\nMultiple address supported, separated by space')
    NanoAddressList = [str(XNO) for XNO in input("Enter receive/refund Nano address: ").split()]
    print("List of XNO address: ", NanoAddressList)
    BananoAddressList = [str(BAN) for BAN in input("Enter receive/refund Banano address: ").split()]
    print("List of BAN address: ", BananoAddressList)

    # sending the information to API to match with user options
    if len(NanoAddressList) == len(BananoAddressList):
        tasks = []
        for i in range(len(NanoAddressList)):
            Number = i+1
            NanoAddress = NanoAddressList[i]
            BananoAddress = BananoAddressList[i]
            if int(user_input) == 1:
                selection = 'buy'
                data = {'coin_address_block': BananoAddress, 'main_refund_address': NanoAddress}
                await api(NanoAddress, BananoAddress, Number, data, selection)
            elif int(user_input) == 2:
                selection = 'sell'
                data = {'address_block': NanoAddress, 'coin_refund_address': BananoAddress}
                await api(NanoAddress, BananoAddress, Number, data, selection)
    else:
        print('Error! Nano Address and Banano Address need to be in the same length!')

# 
async def api(NanoAddress, BananoAddress, Number, data, selection):
    async with aiohttp.ClientSession() as session:
        # use the session to make a POST request
        async with session.post(f'https://banano.nano.trade/{selection}', data=data) as response:
            content = await response.text()
            source = BeautifulSoup(content, "html.parser")
            deposit_address = source.find('input')['value']
            print(f'\nNumber {Number}')
            if selection == 'sell':
                print('------------------------------------------------------------------------------------------------------')
                print(f'Nano receive address: {NanoAddress}')
                print(f'Banano refund address: {BananoAddress}')
                print(f'DEPOSIT ADDRESS: {deposit_address}')
                print('------------------------------------------------------------------------------------------------------')
                print(f'Result: https://nanolooker.com/account/{NanoAddress}\n')
            else:
                print('------------------------------------------------------------------------------------------------------')
                print(f'Banano receive address: {BananoAddress}')
                print(f'Nano refund address: {NanoAddress}')
                print(f'DEPOSIT ADDRESS: {deposit_address}')
                print('------------------------------------------------------------------------------------------------------')
                print(f'Result: https://bananolooker.com/account/{BananoAddress}\n')
                
# run the info function to send all of the requests
loop = asyncio.get_event_loop()
loop.run_until_complete(select())
