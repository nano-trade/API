import json
import requests
from bs4 import BeautifulSoup

# Get price of Banano/Nano pair from banano.nano.trade: (Other pairs are available on nano.trade.)
url='https://banano.nano.trade/api'
getPrice=requests.get(url).json()
print('Price API returns the following JSON: ' + str(getPrice))
print('As an example, get prices (user-buy, user-sell): ' + str(getPrice['user_buy_price']), str(getPrice['user_sell_price']))

# We will buy Banano by sending Nano. Therefore, we'll provide a Banano address to receive Banano, and a Nano refund address. Then we'll get a Nano deposit address to make a deposit.
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36'}
url='https://banano.nano.trade/buy' # /buy is to buy Banano (coin) by selling Nano (main). /sell is to sell Banano to receive Nano. Other pairs are available on nano.trade.

MyBananoAddress='' # Enter your Banano address to receive Banano. 
MyNanoRefundAddress='' # Enter your Nano refund address, that will be used to send a refund when something goes wrong with the transaction (e.g. sending more than the maximum amount).
# This refund address is linked to the given address of the user (MyBananoAddress), it is permanently linked and cannot be changed later.

data={'coin_address_block': MyBananoAddress, 'main_refund_address': MyNanoRefundAddress} # On /sell, the parameters are "address_block" and "coin_refund_address", respectively.
x=requests.post(url, data=data, headers=headers)
source = BeautifulSoup(x.content,"html.parser")
deposit_address=source.find('input')['value']

print('Your deposit address: ' + deposit_address) # You can send the deposit to this address:

print('Your refund address: ' + str(source.findAll('small')[3].text)[65:])

# If you've sent a deposit within 60 minutes after requesting from either /buy or /sell, you don't need to do anything after sending deposits, your transaction will be processed within 2 minutes of your deposit.
# If you don't want to wait 2 minutes, you can directly go to /buying/<address> & /selling/<address>, and see the result of the transation like this:
url='https://banano.nano.trade/buying/' + MyBananoAddress # On /selling, enter your Nano address.
x=requests.get(url, headers=headers)
source = BeautifulSoup(x.content,"html.parser")
result=deposit_address=source.findAll('p')[0].text
print('Result: ' + result) # It should return the exchange rate if the transaction is successful. If not, it should return a "transfer has not arrived yet" message. It may also return a refund message if something goes wrong.
