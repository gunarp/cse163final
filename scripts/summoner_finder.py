import urllib3
import certifi
import pandas as pd
import time
import os


def sum_search(sumid, http, search, api_key):
    r = http.request('GET', search + sumid, headers={'X-Riot-Token': api_key})
    time.sleep(1.5)
    print('Adding summoner ' + sumid)
    return pd.read_json(r.data, typ='series')


def main():
    print('Searching Summoners!')
    api_key = input('Enter API Key:  ')
    league = input('Enter Rank:  ').upper()
    division = input('Enter Division:  ').upper()
    tier_name = league + division

    data = pd.read_csv(os.getcwd() + '\\data\\' + tier_name + '.csv',
                       squeeze=True)
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())
    search = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/'
    sums = data[1:100].apply(sum_search, args=(http, search, api_key))

    sums.to_csv(os.getcwd() + '\\data\\' + tier_name + '_SUMS.csv',
                mode='a', index=False)


if __name__ == '__main__':
    main()
