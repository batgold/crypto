#!/usr/bin/python3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cbpro
import time
from datetime import datetime, timedelta
import numpy as np
import keys
from math import floor, log10
import json

def round_2(x):
    return round(x, -int(floor(log10(abs(x)))))

def Rolling_Average(x, n):
    avg = np.cumsum(x)
    avg[n:] = avg[n:] - avg[:-n]
    avg = avg[n-1:] / n
    return avg

def main():
    days = 150

    start_time = (datetime.now() - timedelta(days)).replace().isoformat()
    start_datetime = datetime.now()-timedelta(days)
    end_time = datetime.now().isoformat()

    auth_client = cbpro.AuthenticatedClient(keys.CBRPO_API_KEY, keys.CBPRO_API_SECRET, keys.CBPRO_API_PASSWORD)
    pub_cli = cbpro.PublicClient()

    coin_val_total = 0
    coin_val_orig_total = 0
    coin = []

    #TODO
    #accts = auth_client.get_accounts()
    #acct = json.loads(json.dumps(accts))
    for x, acct in enumerate(auth_client.get_accounts()):

        if float(acct['balance']) > 0.0:
            if acct['currency'] != 'USD':
                coin.append(acct['currency']+'-USD')

    # PLOT
    fig, ax = plt.subplots(3, 2, sharey=False, sharex=True, gridspec_kw={'hspace':0})
    ax = ax.flatten()

    # LOOP CURRENCIES
    for z, coin_name in enumerate(coin):
        fills = list(auth_client.get_fills(coin_name))         #needs to be a list

        coin_date = []
        coin_size = []
        coin_price = []
        coin_total = 0


        # PRIVATE FILLS
        for fill in fills:
            t = datetime.strptime(fill['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
            t = datetime.fromtimestamp(time.mktime(t.timetuple()))

            if t > start_datetime:
                coin_date.append(t)
                coin_price.append(float(fill['price']))
                coin_size.append(float(fill['size']))
                if fill['side'] == 'sell':
                    coin_size[-1] = -1 * coin_size[-1]
                coin_total = coin_total + coin_size[-1]
                coin_val_orig_total += coin_price[-1] * coin_size[-1]


        # PUBLIC RATES
        coin_rate = pub_cli.get_product_historic_rates(coin_name,start=start_time,end=end_time,granularity=86400)
        coin_rate.sort(key=lambda coin_name: coin_name[0])
        coin_rate = np.array(coin_rate, dtype='object')

        coin_time = []
        for y in coin_rate[:,0]:
            coin_time.append(datetime.fromtimestamp(y))

        coin_rate = coin_rate[:,4]

        coin_avg = Rolling_Average(coin_rate, 20)
        coin_avg_time = coin_time[20-1:]

        coin_val = coin_rate[-1] * coin_total
        coin_val_total += coin_val

        # PRINT TABLES
        # print :coin: :qty: :value:
        print('\n')
        print(fills[0]['product_id'], '{:#.6g}'.format(coin_total), '${:#.2f}'.format(coin_val))
        print('-'*40)

        for x in range(len(coin_size)):
            print(
                coin_date[x].strftime('%d %b %y'),'\t',
                '{:#.6g}'.format(round(coin_price[x],2)),'\t',
                '{:#.6g}'.format(round_2(coin_size[x])),'\t',)


        # CLEAR OUT OLD FILLS (for plotting)
        # decided to not compute original BTC fills from 2017
        #coin_price = [p for x,p in enumerate(coin_price) if coin_date[x] > start_datetime]
        #coin_date = [x for x in coin_date if x > start_datetime]

        # PLOTS
        ax[z].plot(coin_time, coin_rate)
        ax[z].plot(coin_avg_time, coin_avg)
        ax[z].scatter(coin_date, coin_price, marker='*')
        ax[z].xaxis_date()
        ax[z].set(ylabel = coin_name)

        locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax[z].xaxis.set_major_locator(locator)
        ax[z].xaxis.set_major_formatter(formatter)
        ax[z].grid(True)
        if max(coin_rate) < 10:
            ax[z].set_ylim([0, 10])

    print('\n')
    print('-'*40)
    print('START: ${:#.2f}'.format(coin_val_orig_total))
    print('TOTAL: ${:#.2f}'.format(coin_val_total))
    print('% INC: {:#.2f}%'.format(100*coin_val_total/coin_val_orig_total-100))

    plt.show()

if __name__ == '__main__':
    main()
