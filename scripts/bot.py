import urllib3
import certifi
import time
import os
import json
import pytz
import ast
from datetime import datetime
from pytz import timezone
import numpy as np
import pandas as pd

wait_time = 1.22


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
    dest = region + '_' + league + division + '_IDS_' + acct + '.csv'
    if dest not in os.listdir('../data/' + league):
        dest = '../data/' + league + '/' + dest
        all_sums = pd.Series()

        pages_left = True
        page = 1
        while pages_left:
            request = http.request('GET', tier + str(page),
                                   headers={'X-Riot-Token': api_key})
            df = pd.read_json(request.data)

            if 'status' in df.columns:
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
        bot = all_sums.iloc[:len(all_sums.index)//2]
        sample = bot.sample(frac=0.1)
        sample.to_csv(dest, header=False, index=False)
    print('Data for', league, division, 'Gathered by', acct)
    print('Data located @ ', dest)


def gather_sums(acct, api_key, league, division, http, loc, region):
    """
    Uses summoner ids to gather information about players.
    Generates a new csv file which contains player info
    """
    print('Gathering Player Information')
    search = 'https://' + region + \
             '.api.riotgames.com/lol/summoner/v4/summoners/'
    target = '../data/' + league + '/' + region + '_' + league + \
             division + '_IDS_' + acct + '.csv'
    dest = region + '_' + league + division + '_SUMS_' + acct + '.csv'

    if dest not in os.listdir('../data/' + league):
        dest = '../data/' + league + '/' + dest
        data = pd.read_csv(target, squeeze=True, header=None).dropna()

        def sum_search(sumid):
            """
            Helper function for gather_sums.
            Makes a request for each of the summoner ids to gather info
            """
            r = http.request('GET', search + sumid,
                             headers={'X-Riot-Token': api_key})
            if 'status' in str(r.data):
                print('ERROR: status message', end='')
                print(r.data)
                print('Attempting to search again with same API Key')
                time.sleep(wait_time + 0.5)
                return sum_search(sumid)
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
    target = '../data/' + league + '/' + region + '_' + league + \
             division + '_SUMS_' + acct + '.csv'
    dest = region + '_' + league + division + '_MASTERIES_' + acct + '.csv'
    search = 'https://' + region + \
             '.api.riotgames.com/lol/champion-mastery/v4/' + \
             'champion-masteries/by-summoner/'

    if dest not in os.listdir('../data/' + league):
        summoners = pd.read_csv(target).dropna()
        dest = '../data/' + league + '/' + dest

        def masteries_search(sumid):
            """
            Makes requests for gather_masteries
            """
            r = http.request('GET', search + str(sumid),
                             headers={'X-Riot-Token': api_key})
            time.sleep(wait_time)

            result = pd.read_json(r.data, typ='series')[0:5]
            if len(result) < 5:
                for i in range(len(result), 5):
                    result = result.append(pd.Series({i: np.nan}))

            return result

        m = summoners['id'].apply(masteries_search)
        for i in range(5):
            summoners['c' + str(i+1)] = m[i]

        summoners.to_csv(dest, index=False)

    print('Masteries all found!')


def gather_matches(acct, api_key, league, division, http, loc, region):
    """
    Gathers last 8 match ids for each summoner
    """
    print('Gathering Match Information')
    search = 'https://' + region + '.api.riotgames.com' + \
             '/lol/match/v4/matchlists/by-account/'
    target = '../data/' + league + '/' + region + '_' + league + \
             division + '_MASTERIES_' + acct + '.csv'
    dest = region + '_' + league + division + '_MATCHES_' + acct + '.csv'
    summoners = pd.read_csv(target)
    if 'status' in summoners.columns:
        summoners = summoners.drop('status', axis=1).dropna()
    summoners = summoners.dropna()

    if dest not in os.listdir('../data/' + league):
        dest = '../data/' + league + '/' + dest

        def match_search(acctid):
            """
            Gathers a match list
            """
            r = http.request('GET', search + str(acctid) + '?queue=420',
                             headers={'X-Riot-Token': api_key})
            m_list = pd.read_json(r.data)[0:8]

            if 'status' in m_list.columns:
                print('ERROR: status message', end='')
                print(r.data)
                print('Attempting to search again with same API Key')
                time.sleep(wait_time + 0.5)
                return match_search(acctid)

            m_list = m_list['matches']
            time.sleep(wait_time)
            return m_list

        matches = summoners['accountId'].apply(match_search)
        for i in range(8):
            summoners['m' + str(i+1)] = matches[i]

        summoners.to_csv(dest, index=False)

    print('Match list gathered! Data saved.')


def fill_matches(acct, api_key, league, division, http, loc, region):
    """
    Gathers information for summoner's last 8 matches
    """
    search = 'https://' + region + '.api.riotgames.com/lol/match/v4/matches/'
    mask = ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8']
    print('Filling matches!')
    target = '../data/' + league + '/' + region + '_' + \
             league + division + '_MATCHES_' + acct + '.csv'
    dest = '../data/' + league + '/' + region + '_' + league + \
           division + '_MATCHINFO_' + acct + '.csv'

    def resume(target):
        print('resuming work!')
        d = region + '_' + league + division + '_MATCHINFO_' + acct + '.csv'
        if d not in os.listdir('../data/' + league):
            return pd.read_csv(target)
        done = pd.read_csv(dest).shape[0]
        return pd.read_csv(target).iloc[done:]

    summoners = resume(target)
    if 'status' in summoners.columns:
        summoners = summoners.drop('status', axis=1).dropna()
    summoners = summoners.dropna()

    def match_fill(summoner):
        """
        Takes a match list and creates a detailed list of match data
        """
        def match_grab(match):
            """
            Helper method to match_fill. Makes the requests for each match
            """
            match = ast.literal_eval(match)
            match = match['gameId']
            r = http.request('GET', search + str(match),
                             headers={'X-Riot-Token': api_key})
            time.sleep(wait_time)

            if 'status' in str(r.data):
                print('Unwanted response: ', end='')
                print(r.data)
                print('Attempting to search again with same API Key')
                time.sleep(wait_time + 0.5)
                return match_grab(match)

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

    date_format = '%m/%d/%Y %H:%M:%S %Z'
    date = datetime.now(tz=pytz.utc).astimezone(timezone('US/Pacific'))

    print('Using', acct, 'to find', league, division)
    print()

    print(date.strftime(date_format))
    gather_ranks(acct, api_key, league, division, http, loc, region)
    print()

    print(date.strftime(date_format))
    gather_sums(acct, api_key, league, division, http, loc, region)
    print()

    print(date.strftime(date_format))
    gather_masteries(acct, api_key, league, division, http, loc, region)
    print()

    print(date.strftime(date_format))
    gather_matches(acct, api_key, league, division, http, loc, region)
    print()

    print(date.strftime(date_format))
    fill_matches(acct, api_key, league, division, http, loc, region)
    print()

    print('All done!')


if __name__ == '__main__':
    main()
