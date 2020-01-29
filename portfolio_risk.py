#Packages
import pandas as pd
import numpy as np
import robin_stocks as r
import getpass
from yahoofinancials import YahooFinancials

#Access RobinHood
username = input("Enter your RobinHood username: ")
password = getpass.getpass("Enter your RobinHood password: ")
login = r.login(username,password)

#Access account information and build data
info=r.account.build_holdings()
raw_data = pd.DataFrame(info)
stock_info = raw_data.iloc[0:2]
stock_info = stock_info.transpose()
num_in_portfolio = len(stock_info.index)

#Quick stock calculations
stock_info['price'] = stock_info['price'].astype('float')
stock_info['quantity'] = stock_info['quantity'].astype('float')
stock_info['Total_Invested'] = stock_info['price'].astype('float') * stock_info['quantity'].astype('float')
stock_sum = sum(stock_info['Total_Invested'])

#Finding betas for all portfolio holdings
row_names = stock_info.index.values
row_names = list(row_names)
stockbeta = []

for ticker in row_names:
    new_beta = YahooFinancials(ticker).get_beta()
    if new_beta is None:
        new_beta = 1
    stockbeta.append(new_beta)

# Calculate portfolio Beta

stockbeta = pd.DataFrame(stockbeta)
stockbeta = stockbeta.rename(columns={0: "betas"})
stockbeta['names'] = row_names
stockbeta = stockbeta.set_index("names")

stockvar = stockbeta['betas']
stocknewinfo = stock_info['Total_Invested']

portfolio_beta = sum((stocknewinfo/stock_sum) * stockvar)

# Gather more portfolio and market return data

riskfreerate = .0156
x = YahooFinancials("^GSPC").get_historical_price_data('2019-01-29','2020-01-29','monthly')

for y in x['^GSPC']['prices'][:-11]:
    startprice = y['close']

for y in x['^GSPC']['prices'][:11]:
    endprice = y['close']

market_return = (endprice - startprice) / startprice

# Calculate expected rate of return

expected_ror = riskfreerate + portfolio_beta * (market_return - riskfreerate)

# Gather more portfolio information
stocksreturn = []

for ticker in row_names:
    pastprice = r.get_historicals(ticker, 'year')
    pastprice = pd.DataFrame(pastprice)
    pastpriceamt = pastprice['close_price'].astype('float').values[0]
    currprice = r.get_historicals(ticker,'day')
    currprice = pd.DataFrame(currprice)
    currpriceamt = currprice['close_price'].astype('float').values[0]
    stock_return = (currpriceamt - pastpriceamt) / pastpriceamt
    stocksreturn.append(stock_return)

# Calculate portfolio profit % based on weighted returns

stocksreturn = pd.DataFrame(stocksreturn)
stocksreturn = stocksreturn.rename(columns={0: "returns"})
stocksreturn['names'] = row_names
stocksreturn = stocksreturn.set_index("names")
newreturnval = stocksreturn['returns']
weightedval = sum((stocknewinfo/stock_sum) * newreturnval)

portfolio_alpha = weightedval - expected_ror

print('Your portfolio alpha is: ' + str(portfolio_alpha))
print('Your portfolio beta is: ' + str(portfolio_beta))
