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


def gather_ranks(acct, api_key, league, division, http, loc):
    """
    Gather all summoner keys of specified rank.
    Genreates two csv files, one containing all summoner ids and one
    containing a randomly sampled 10% of summoner ids to use for investigation.
    """
    print('Gathering ids from league')
    tier = 'https://na1.api.riotgames.com/lol/league/v4/entries/' + \
           'RANKED_SOLO_5x5/' + league + '/' + division + '?page='
    dest_file = '../data/' + league + division + '_IDS_' + acct + '.csv'
    all_sums = pd.Series()

    pages_left = True
    page = 1
    while pages_left:
        request = http.request('GET', tier + str(page),
                               headers={'X-Riot-Token': api_key})
        df = pd.read_json(request.data)

        if (len(df) > 0):
            all_sums = all_sums.append(df['summonerId'], ignore_index=True)
            #print('Added page ' + str(page))
            time.sleep(wait_time)
        else:
            pages_left = False
            break
        page += 1
    sample = all_sums.sample(frac=0.1)
    sample.to_csv(dest_file, header=False, index=False)
    print('Data for', league, division, 'Gathered by', acct)
    print('Data located @ ', dest_file)


def gather_sums(acct, api_key, league, division, http, loc):
    """
    Uses summoner ids to gather information about players.
    Generates a new csv file which contains player info
    """
    print('Gathering Player Information')
    search = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/'
    target = '../data/' + league + division + '_IDS_' + acct + '.csv'
    data = pd.read_csv(target, squeeze=True, header=None)

    def sum_search(sumid):
        """
        Helper function for gather_sums.
        Makes a request for each of the summoner ids to gather info
        """
        r = http.request('GET', search + sumid,
                         headers={'X-Riot-Token': api_key})
        #print('Added summoner ' + sumid)
        time.sleep(wait_time)
        return pd.read_json(r.data, typ='series')

    sums_info = data.apply(sum_search)
    sums_info.to_csv('../data/' + league + division +
                     '_SUMS_' + acct + '.csv', index=False)
    print('Done gathering player info!')


def gather_masteries(acct, api_key, league, division, http, loc):
    """
    Gathers player champion mastery data. Grabs top five champions
    """
    print('Gathering Champion Masteries')
    target = '../data/' + league + division + '_SUMS_' + acct + '.csv'
    search = 'https://na1.api.riotgames.com/lol/champion-mastery/v4/' + \
             'champion-masteries/by-summoner/'
    summoners = pd.read_csv(target)
    def masteries_search(sumid):
        """
        Makes requests for gather_masteries
        """
        r = http.request('GET', search + str(sumid),
                         headers={'X-Riot-Token': api_key})
        #print('Found masteries for', sumid)
        time.sleep(wait_time)

        result = pd.read_json(r.data, typ='series')[0:5]
        if len(result) < 5:
            for i in range(len(result), 5):
                result = result.append(pd.Series({i: np.nan}))

        return result

    m = summoners['id'].apply(masteries_search)
    #summoners = summoners.assign(c1=m[0], c2=m[1], c3=m[2],
    #                             c4=m[3], c5=m[4])
    summoners['c1'] = m[0]
    summoners['c2'] = m[1]
    summoners['c3'] = m[2]
    summoners['c4'] = m[3]
    summoners['c5'] = m[4]

    summoners.to_csv('../data/' + league + division +
                     '_MASTERIES_' + acct + '.csv', index=False)
    print('Masteries all found!')


def gather_matches(acct, api_key, league, division, http, loc):
    """
    Gathers last 8 match ids for each summoner
    """
    print('Gathering Match Information')
    search = 'https://na1.api.riotgames.com' + \
             '/lol/match/v4/matchlists/by-account/'
    target = '../data/' + league + division + \
        '_SUMS_' + acct + '.csv'
    summoners = pd.read_csv(target)

    def match_search(acctid):
        """
        Gathers a match list
        """
        r = http.request('GET', search + acctid + '?queue=420',
                         headers={'X-Riot-Token': api_key})
        m_list = pd.read_json(r.data)[0:8]
        m_list = m_list['matches']
        #print('Added matches for ' + acctid)
        time.sleep(wait_time)
        return m_list

    matches = summoners['accountId'].apply(match_search)
    summoners = summoners.assign(m1=matches[0], m2=matches[1],
                                 m3=matches[2], m4=matches[3],
                                 m5=matches[4], m6=matches[5],
                                 m7=matches[6], m8=matches[7])
    summoners['m1'] = matches[0]
    summoners['m2'] = matches[1]
    summoners['m3'] = matches[2]
    summoners['m4'] = matches[3]
    summoners['m5'] = matches[4]
    summoners['m6'] = matches[5]
    summoners['m7'] = matches[6]
    summoners['m8'] = matches[7]

    summoners.to_csv('../data/' + league + division +
                     '_MATCHES_' + acct + '.csv', index=False)
    print('Match list gathered! Data saved.')


def fill_matches(acct, api_key, league, division, http, loc):
    """
    Gathers information for summoner's last 8 matches
    """
    search = 'https://na1.api.riotgames.com/lol/match/v4/matches/'
    mask = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8']
    print('Filling matches!')
    target = '../data/' + league + division + \
        '_MATCHES_' + acct + '.csv'
    summoners = pd.read_csv(target)

    def match_fill(summoner):
        """
        Takes a match list and creates a detailed list of match data
        """
        def match_grab(match):
            """
            Helper method to match_fill. Makes the requests for each match
            """
            gid = ast.literal_eval(match)['gameId']
            r = http.request('GET', search + str(gid),
                             headers={'X-Riot-Token': api_key})
            time.sleep(wait_time)
            return json.loads(r.data)

        return summoner.apply(match_grab)

    match_details = summoners.loc[:, mask].apply(match_fill, axis=1)
    #match_details.columns += '_info'
    #summoners = summoners.merge(match_details,
    #                            left_index=True, right_index=True)

    summoners['m1'] = match_details['m1']
    summoners['m2'] = match_details['m2']
    summoners['m3'] = match_details['m3']
    summoners['m4'] = match_details['m4']
    summoners['m5'] = match_details['m5']
    summoners['m6'] = match_details['m6']
    summoners['m7'] = match_details['m7']
    summoners['m8'] = match_details['m8']

    summoners.to_csv('../data/' + league + division +
                     acct + '.csv', index=False)
    print('Match Data complete!')


def main():
    print('Welcome to the crazy data gather party')
    acct = input('Enter your username: ')
    api_key = input('Enter API Key:  ')
    league = input('Enter League: ').upper()
    division = input('Enter Division: ').upper()
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())
    loc = os.getcwd()
    print('Using', acct, 'to find', league, division)
    print()
    """     
    print(datetime.datetime.now())
    gather_ranks(acct, api_key, league, division, http, loc)
    print()

    print(datetime.datetime.now())
    gather_sums(acct, api_key, league, division, http, loc)
    print()
 
    print(datetime.datetime.now())
    gather_masteries(acct, api_key, league, division, http, loc)
    print()
    """    
    print(datetime.datetime.now())
    gather_matches(acct, api_key, league, division, http, loc)
    print()    
   
    print(datetime.datetime.now())
    fill_matches(acct, api_key, league, division, http, loc)
    print()

    print('All done!')

if __name__ == '__main__':
    main()







