import urllib3
import certifi
import pandas as pd
import time
import os

wait_time = 1.2


def gather_ranks(acct, api_key, league, division, http, loc):
    """
    Gather all summoner keys of specified rank.
    Genreates two csv files, one containing all summoner ids and one
    containing a randomly sampled 10% of summoner ids to use for investigation.
    """
    tier = 'https://na1.api.riotgames.com/lol/league/v4/entries/' + \
           'RANKED_SOLO_5x5/' + league + '/' + division + '?page='
    dest_file = loc + '\\data\\' + league + division + '_ids_' + acct + '.csv'
    all_sums = pd.DataFrame()

    pages_left = True
    page = 1
    while pages_left:
        request = http.request('GET', tier + str(page),
                               headers={'X-Riot-Token': api_key})
        df = pd.read_json(request.data)

        if (len(df) > 0):
            all_sums.append(df['smmonerId'], ignore_index=True)
            print('Added page ' + str(page), end='')
            time.sleep(wait_time)
        else:
            pages_left = False
            break
        page += 1
    sample = all_sums.sample(frac=0.1)
    sample.to_csv(dest_file)
    print('Data for', league, division, 'Gathered by', acct)
    print('Data located @ ', dest_file)


def gather_sums(acct, api_key, league, division, http, loc):
    """
    Uses summoner ids to gather information about players.
    Generates a new csv file which contains player info
    """
    search = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/'
    target = loc + '\\data\\' + league + division + '_ids_' + acct + '.csv'
    data = pd.read_csv(target, squeeze=True)

    def sum_search(sumid):
        """
        Helper function for gather_sums.
        Makes a request for each of the summoner ids to gather info
        """
        r = http.request('GET', search + sumid,
                         headers={'X-Riot-Token': api_key})
        print('Added summoner ' + sumid)
        time.sleep(wait_time)
        return pd.read_json(r.data, typ='series')

    sums_info = data.apply(sum_search)
    sums_info.to_csv(loc + '\\data\\' + league + division +
                     '_SUMS_' + acct + '.csv')


def main():
    print('Welcome to the crazy data gather party')
    acct_name = input('Enter your username')
    api_key = input('Enter API Key:  ')
    league = input('Enter League: ').upper()
    division = input('Enter Division: ').upper()
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())
    loc = os.getcwd()

    gather_ranks(acct_name, api_key, league, division, http, loc)
    gather_sums(acct_name, api_key, league, division, http, loc)
    # gather_matches()
    # gather_masteries()


if __name__ == '__main__':
    main()
