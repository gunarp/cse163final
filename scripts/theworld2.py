import urllib3
import certifi
import time
import os
import json
import ast
import datetime
import numpy as np
import pandas as pd

wait_time = 1.23


def resume(target, current):
    """
    Picks up where we left off!
    Takes in two strings, an input and output file. Returns
    a dataframe containing the remaining input needed.
    """
    if current not in set(os.listdir('../data')):
        return pd.read_csv(target)
    target = pd.read_csv(target)
    current = pd.read_csv(current)
    return target[current.shape[0]:]


def gather_ranks(acct, api_key, league, division, http, loc, region):
    """
    Gather all summoner keys of specified rank.
    Genreates two csv files, one containing all summoner ids and one
    containing a randomly sampled 10% of summoner ids to use for investigation.
    """
    print('Gathering ids from league')
    tier = 'https://' + region + '.api.riotgames.com' + \
           '/lol/league/v4/entries/RANKED_SOLO_5x5/' + \
           league + '/' + division + '?page='
    dest_file = '../data/' + region + '_' + league + \
                division + '_IDS_' + acct + '.csv'
    all_sums = pd.Series()

    pages_left = True
    page = 1
    while pages_left:
        request = http.request('GET', tier + str(page),
                               headers={'X-Riot-Token': api_key})
        df = pd.read_json(request.data)

        if (len(df) > 0):
            all_sums = all_sums.append(df['summonerId'], ignore_index=True)
            # print('Added page ' + str(page))
            time.sleep(wait_time)
        else:
            pages_left = False
            break
        page += 1
    sample = all_sums.sample(frac=0.1)
    sample.to_csv(dest_file, header=False, index=False)
    print('Data for', league, division, 'Gathered by', acct)
    print('Data located @ ', dest_file)


def gather_sums(acct, api_key, league, division, http, loc, region):
    """
    Uses summoner ids to gather information about players.
    Generates a new csv file which contains player info
    """
    print('Gathering Player Information')
    search = 'https://' + region + \
             '.api.riotgames.com/lol/summoner/v4/summoners/'
    target = '../data/' + region + '_' + league + \
             division + '_IDS_' + acct + '.csv'
    dest = '../data/' + region + '_' + league + \
           division + '_SUMS_' + acct + '.csv'
    data = pd.read_csv(target, squeeze=True, header=None)

    def sum_search(sumid):
        """
        Helper function for gather_sums.
        Makes a request for each of the summoner ids to gather info
        """
        r = http.request('GET', search + sumid,
                         headers={'X-Riot-Token': api_key})
        # print('Added summoner ' + sumid)
        time.sleep(wait_time)
        return pd.read_json(r.data, typ='series')

    sums_info = data.apply(sum_search)
    sums_info.to_csv(dest, index=False)
    print('Done gathering player info!')


def gather_masteries(acct, api_key, league, division, http, loc, region):
    """
    Gathers player champion mastery data. Grabs top five champions
    """
    print('Gathering Champion Masteries')
    target = '../data/' + region + '_' + league + \
             division + '_SUMS_' + acct + '.csv'
    dest = '../data/' + region + '_' + league + \
           division + '_MASTERIES_' + acct + '.csv'
    search = 'https://' + region + \
             '.api.riotgames.com/lol/champion-mastery/v4/' + \
             'champion-masteries/by-summoner/'
    summoners = resume(target, dest)

    def masteries_search(sumid):
        """
        Makes requests for gather_masteries
        """
        r = http.request('GET', search + str(sumid),
                         headers={'X-Riot-Token': api_key})
        # print('Found masteries for', sumid)
        time.sleep(wait_time)

        result = pd.read_json(r.data, typ='series')[0:5]
        if len(result) < 5:
            for i in range(len(result), 5):
                result = result.append(pd.Series({i: np.nan}))

        result.to_csv(dest, index=False, mode='a+')

    summoners['id'].apply(masteries_search)

    print('Masteries all found!')


def gather_matches(acct, api_key, league, division, http, loc, region):
    """
    Gathers last 8 match ids for each summoner
    """
    print('Gathering Match Information')
    search = 'https://' + region + '.api.riotgames.com' + \
             '/lol/match/v4/matchlists/by-account/'
    target = '../data/' + region + '_' + league + \
             division + '_SUMS_' + acct + '.csv'
    dest = '../data/' + region + '_' + league + \
           division + '_MATCHES_' + acct + '.csv'
    summoners = pd.read_csv(target)

    def match_search(acctid):
        """
        Gathers a match list
        """
        r = http.request('GET', search + acctid + '?queue=420',
                         headers={'X-Riot-Token': api_key})
        m_list = pd.read_json(r.data)[0:8]
        m_list = pd.DataFrame(m_list['matches']).transpose()
        m_list.to_csv(dest, mode='a+', index=False, header=False)
        time.sleep(wait_time)

    summoners['accountId'].apply(match_search)
    print('Match list gathered! Data saved.')


def fill_matches(acct, api_key, league, division, http, loc, region):
    """
    Gathers information for summoner's last 8 matches
    """
    search = 'https://' + region + '.api.riotgames.com/lol/match/v4/matches/'
    mask = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8']
    print('Filling matches!')
    target = '../data/' + region + '_' + region + '_' + league + division + \
        '_MATCHES_' + acct + '.csv'
    dest = '../data/' + region + '_' + league + \
           division + '_MATCHINFO_' + acct + '.csv'

    def clean(row):
        if '0' in row.values or 0 in row.values:
            return np.nan

        def extract(col):
            return ast.literal_eval(col[0])['gameId']
        return row.apply(extract)

    summoners = pd.read_csv(target).apply(clean, axis=1)

    def match_fill(summoner):
        """
        Takes a match list and creates a detailed list of match data
        """
        def match_grab(match):
            """
            Helper method to match_fill. Makes the requests for each match
            """
            r = http.request('GET', search + str(match),
                             headers={'X-Riot-Token': api_key})
            time.sleep(wait_time)
            return json.loads(r.data)

        summoner.apply(match_grab).to_csv(dest, index=False, mode='a+')

    summoners.loc[:, mask].apply(match_fill, axis=1)

    print('Match Data complete!')


def main():
    print('Welcome to the crazy data gather party')
    acct = input('Enter your username: ')
    api_key = input('Enter API Key:  ')
    league = input('Enter League: ').upper()
    division = input('Enter Division: ').upper()
    region = input('Enter Region: ').upper()
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())
    loc = os.getcwd()
    print('Using', acct, 'to find', league, division)
    print()

    print(datetime.datetime.now())
    #gather_ranks(acct, api_key, league, division, http, loc, region)
    print()

    print(datetime.datetime.now())
    #gather_sums(acct, api_key, league, division, http, loc, region)
    print()

    print(datetime.datetime.now())
    #gather_masteries(acct, api_key, league, division, http, loc, region)
    print()

    print(datetime.datetime.now())
    gather_matches(acct, api_key, league, division, http, loc, region)
    print()

    print(datetime.datetime.now())
    fill_matches(acct, api_key, league, division, http, loc, region)
    print()

    print('All done!')


if __name__ == '__main__':
    main()
