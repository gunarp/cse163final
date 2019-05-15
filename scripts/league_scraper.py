import urllib3
import certifi
import pandas as pd
import time
import os


def main():
    # Fields
    api_key = input('Enter API Key:  ')
    league = input('Enter League: ').upper()
    division = input('Enter Division: ').upper()
    tier_name = league + division

    num_pages_left = 500
    ppm = 100
    start_page = 1

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())

    # Request Endpoint
    tier = 'https://na1.api.riotgames.com/lol/league/v4/entries/' + \
           'RANKED_SOLO_5x5/' + league + '/' + division + '?page='

    while num_pages_left > 0:
        g1_info = pd.Series()
        if num_pages_left < ppm:
            n = num_pages_left + start_page
        else:
            n = ppm + start_page

        for i in range(start_page, n):
            request = http.request('GET', tier + str(i),
                                   headers={'X-Riot-Token': api_key})
            df = pd.read_json(request.data)
            if (len(df) > 0):
                g1_info = g1_info.append(df['summonerId'], ignore_index=True)
                print('Added page ' + str(i), end='')
                time.sleep(0.5)
                print(' .', end='')
                time.sleep(0.5)
                print(' .')
                time.sleep(0.5)
            else:
                num_pages_left = n-1
                break

        start_page = n
        num_pages_left -= (n-1)

        g1_info.to_csv(os.getcwd() + '\\data\\' + tier_name + '.csv', mode='a',
                       header=False, index=False)

        # print('sleeping, ' + str(num_pages_left) +
        #       ' pages remaining', end='')
        # for j in range(24):
        #     time.sleep(5)
        #     print(' .', end='')
        # print('')

    print('Data gathered!')


if __name__ == '__main__':
    main()
