#!/usr/bin/python3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cbpro
import time
from datetime import datetime, timedelta
import numpy as np
import keys

days = 90

start_time = (datetime.now() - timedelta(days)).replace().isoformat()
start_datetime = datetime.now()-timedelta(days)
end_time = datetime.now().isoformat()

auth_client = cbpro.AuthenticatedClient(keys.CBRPO_API_KEY,
        keys.CBPRO_API_SECRET, keys.CBPRO_API_PASSWORD)
pub_cli = cbpro.PublicClient()

a=auth_client.get_accounts()
#a = auth_client.get_account('1bce17f4e758880e72959f940d8febd7')
#a = auth_client.get_account_history('1bce17f4e758880e72959f940d8febd7')

curr = []
for x, acct in enumerate(a):
    if float(acct['balance']) > 0.0:
        if acct['currency'] != 'USD':
            curr.append(acct['currency']+'-USD')

print(curr)
#fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(3, 2, sharey=False)
fig, ax = plt.subplots(3, 2, sharey=False, sharex=True, gridspec_kw={'hspace':0})

ax = ax.flatten()

for z,x in enumerate(curr):
    a = auth_client.get_fills(x)
#a = auth_client.get_fills('BTC-USD')
#print(a[3]['balance'])

    a = list(a)
    print(a[0]['product_id'])
    print(a[0]['price'])
    t_btc_buy = a[0]['created_at']

    btc_date=[]
    btc_price=[]
    btc_size = []

    for fills in a:
        t=time.mktime(datetime.strptime(fills['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ').timetuple())
        t=datetime.fromtimestamp(t)
        if t > start_datetime:
        #btc_date.append(datetime.strptime(fills['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ').date())
            btc_date.append(t)
            btc_price.append(float(fills['price']))
            #btc_size.append(float(fills['size']))
            size = float(fills['size'])

    btc = pub_cli.get_product_historic_rates(x,start=start_time,end=end_time,granularity=86400)
    btc.sort(key=lambda x: x[0])
    btc = np.array(btc, dtype='object')

    t_btc = []
    for y in btc[:,0]:
        #t_btc.append(datetime.fromtimestamp(y).strftime('%m-%d'))
        t_btc.append(datetime.fromtimestamp(y))

    #t = btc[:,0]
    btc = btc[:,4]

    btc_avg = np.cumsum(btc)
    #average
    n=20
    btc_avg[n:] = btc_avg[n:] - btc_avg[:-n]
    btc_avg = btc_avg[n-1:]/n
    t_btc_avg = t_btc[n-1:]

    ax[z].plot(t_btc, btc)
    ax[z].plot(t_btc_avg, btc_avg)
    ax[z].scatter(btc_date,btc_price,marker='*')
    ax[z].xaxis_date()

    #ax.set(xlabel='date' ylabel='$' title='btc')
    #ax[z].set_title('ok')
    ax[z].set(ylabel=x+' '+str(size))

    #ax[z].set_xticks(np.arange(0,len(btc),days/10))
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    ax[z].xaxis.set_major_locator(locator)
    ax[z].xaxis.set_major_formatter(formatter)
    ax[z].grid(True)

plt.show()
