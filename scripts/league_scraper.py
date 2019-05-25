import urllib3
import certifi
import pandas as pd
import time
import os


def main():
    # Fields
    print('Finding Summoner ids')
    api_key = input('Enter API Key:  ')
    league = input('Enter League: ').upper()
    division = input('Enter Division: ').upper()
    tier_name = league + division

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())

    # Request Endpoint
    tier = 'https://na1.api.riotgames.com/lol/league/v4/entries/' + \
           'RANKED_SOLO_5x5/' + league + '/' + division + '?page='
    all_sums = pd.DataFrame()
    pages_left = True
    page = 1
    while pages_left:
        request = http.request('GET', tier + str(page),
                               headers={'X-Riot-Token': api_key})
        df = pd.read_json(request.data)

        if (len(df) > 0):
            # info = info.append(df['summonerId'], ignore_index=True)
            all_sums.append(df['summonerId'], ignore_index=True)
            print('Added page ' + str(page), end='')
            time.sleep(0.5)
            print(' .', end='')
            time.sleep(0.5)
            print(' .')
            time.sleep(0.5)
            # info.to_csv(os.getcwd() + '\\data\\' + tier_name + '.csv',
            #             mode='a', header=False, index=False)
        else:
            pages_left = False
            break
        page += 1
    all_sums.to_csv(os.getcwd() + '\\data\\' + tier_name + '.csv',
                    mode='a', header=False, index=False)
    print('Data gathered!')


if __name__ == '__main__':
    main()
