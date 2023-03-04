import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio

# promps user to select an option
async def select():
    options = ['Buy Banano', 'Sell Banano'];
    user_input = '';
    input_message = "Pick an option:\n"

    for index, item in enumerate(options):
        input_message += f'{index+1}) {item}\n'
    input_message += 'Your choice: '

    while user_input not in map(str, range(1, len(options) + 1)):
        user_input = input(input_message)
    print(f'You picked: {options[int(user_input) - 1]}')
    # get quotes from API and parse for user
    getPrice=requests.get('https://banano.nano.trade/api').json()
    print('\nBuy Price: 1 NANO:' + str(round(1 / getPrice['user_buy_price'], 2)) + ' BANANO - Max Buy: ' + "{:,}".format(getPrice['max_buy']) + ' NANO')
    print('Sell Price: ' + str(round(1 / getPrice['user_sell_price'], 2)) + ' BANANO:1 NANO - Max Sell: ' + "{:,}".format(getPrice['max_sell']) + ' BANANO')

    # user defined list of single or multiple address, have to put two if statements cause it is not working? bug?
    print('\nMultiple address supported, separated by space')
    while True:
        NanoAddressList = [str(XNO) for XNO in input("Enter receive/refund Nano address: ").split()]
        for i in NanoAddressList:
            length = len(i)
            NanoAddressCheck = int(i.find('nano_'))
        if length < 65:
            print('Sorry, not a valid Nano address.')
        else:
            if NanoAddressCheck < 0:
                print('Sorry, not a valid Nano address.')
            else:
            #we're happy with the value given and ready to exit the loop.
                print("List of XNO address: ", NanoAddressList)
                break

    while True:
        BananoAddressList = [str(BAN) for BAN in input("\nEnter receive/refund Banano address: ").split()]
        for i in BananoAddressList:
            length = len(i)
            BananoAddressCheck = i.find('ban_')
        if length < 64:
            print('Sorry, not a valid Banano address.')
        else:
            if BananoAddressCheck < 0:
                print('Sorry, not a valid Banano address.')
            else:
            #we're happy with the value given and ready to exit the loop.
                print("List of BAN address: ", BananoAddressList)
                break

    # checking the user input and sent the information to the API
    if len(NanoAddressList) == len(BananoAddressList):
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
        print('Error! Nano Address and Banano Address must have the same length!')

# process the request, sanitize the input and return deposit and address     
async def api(NanoAddress, BananoAddress, Number, data, selection):
    async with aiohttp.ClientSession() as session:
        # use the session to make a POST request
        async with session.post(f'https://banano.nano.trade/{selection}', data=data) as response:
            content = await response.text()
            source = BeautifulSoup(content, "html.parser")
            sourcesanitize = 'id="address'
            if sourcesanitize in content:
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
            else:
                print('\nServer error or incorrect address, try again!')
                
# run the info function to send all of the requests
loop = asyncio.get_event_loop()
loop.run_until_complete(select())


