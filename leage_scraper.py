import urllib3
import certifi
import pandas as pd
import time
import os

def main():
    # Fields PLEASE CHANGE API_KEY
    api_key = 'RGAPI-6481d673-e9a0-4302-b348-4384e5db7ca7'
    num_pages_left = 500
    ppm = 100
    start_page = 1

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    # Request Endpoint
    tier = 'https://na1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/GOLD/II?page='
    tier_name = 'g2'

    while num_pages_left > 0:
        g1_info = pd.Series()
        if num_pages_left < ppm:
            n = num_pages_left + start_page
        else:
            n = ppm + start_page

        for i in range(start_page, n):
            request = http.request('GET', tier + str(i), headers={'X-Riot-Token':api_key})
            df = pd.read_json(request.data)
            if (len(df) > 0):
                g1_info = g1_info.append(df['summonerId'], ignore_index=True)
                print('Added page ' + str(i), end='')
                time.sleep(1.4/3)
                print(' .', end='')
                time.sleep(1.4/3)
                print(' .')
                time.sleep(1.4/3)
            else:
                num_pages_left = n-1
                break

        start_page = n
        num_pages_left -= (n-1)
        
        g1_info.to_csv(os.getcwd() + '\\' + tier_name + '.csv', mode='a', header=False, index=False)

        # print('sleeping, ' + str(num_pages_left) + ' pages remaining', end='')
        # for j in range(24):
        #     time.sleep(5)
        #     print(' .', end='')
        # print('')
    
    
    print('Data gathered!')


if __name__ == '__main__':
    main()