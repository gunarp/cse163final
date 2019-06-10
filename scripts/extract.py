# Takes our raw csv data files and creates a new csv of the data we care about

import pandas as pd
import numpy as np
import ast


def retrieve_icon_rows(data):
    """
    Takes a pandas data frame and returns a dataframe with
    only rows with valid icon numbers
    """
    purple = data['profileIconId'] == 4087
    red = data['profileIconId'] == 4086
    blue = data['profileIconId'] == 4089
    green = data['profileIconId'] == 4088

    specific = data[purple | red | blue | green]
    specific = specific.reset_index(drop=True)
    return specific


def add_rows(data):
    """
    takes a specific dataframe and adds columns to the
    dataframe. These columns contain the data we need
    """
    specific = data.assign(champ=0, kills=0, deaths=0, assists=0, time_alive=0,
                           percent_champ_dmg=0, total_heal=0,
                           units_healed=0, self_mitigated=0, obj_dmg=0,
                           turr_dmg=0, vis_score=0, dmg_taken=0, gold_earned=0,
                           minions_killed=0, wards_placed=0, wards_killed=0,
                           first_blood=0, first_tower=0)
    return specific


def get_data(specific):
    """
    iterates over entire dataframe and retrieves valid data.
    adds this data to the new columns and calculates averages, modes,
    or max at the end of each row
    """
    for index, row in specific.iterrows():
        print(index)
        specific.loc[index, 'champ'] =\
            ast.literal_eval(specific.loc[index, 'c1'])['championId']
        name = specific.at[index, 'name']
        count = 0
        for game in range(8):
            game_string = specific.at[index, str(game)]
            try:
                info = ast.literal_eval(game_string)
            except ValueError:
                break
            if 'status' in info:
                break
            if info['gameDuration'] < 300:
                break
            num = None
            for i in range(10):
                s = 'participantIdentities'
                if info[s][i]['player']['summonerName'] == name:
                    num = i
            if num is None:
                break
            part_info = info['participants'][num]['stats']
            if part_info['totalDamageDealt'] == 0:
                break
            count += 1
            specific.loc[index, 'kills'] +=\
                part_info['kills']
            specific.loc[index, 'deaths'] +=\
                part_info['deaths']
            specific.loc[index, 'assists'] +=\
                part_info['assists']
            specific.loc[index, 'time_alive'] +=\
                part_info['longestTimeSpentLiving']
            specific.loc[index, 'percent_champ_dmg'] +=\
                part_info['totalDamageDealtToChampions'] /\
                part_info['totalDamageDealt']
            specific.loc[index, 'total_heal'] +=\
                part_info['totalHeal']
            specific.loc[index, 'units_healed'] +=\
                part_info['totalUnitsHealed']
            specific.loc[index, 'self_mitigated'] +=\
                part_info['damageSelfMitigated']
            specific.loc[index, 'obj_dmg'] +=\
                part_info['damageDealtToObjectives']
            specific.loc[index, 'turr_dmg'] +=\
                part_info['damageDealtToTurrets']
            specific.loc[index, 'vis_score'] +=\
                part_info['visionScore']
            specific.loc[index, 'dmg_taken'] +=\
                part_info['totalDamageTaken']
            specific.loc[index, 'gold_earned'] +=\
                part_info['goldEarned']
            specific.loc[index, 'minions_killed'] +=\
                part_info['totalMinionsKilled']
            specific.loc[index, 'wards_placed'] +=\
                part_info['wardsPlaced']
            specific.loc[index, 'wards_killed'] +=\
                part_info['wardsKilled']
            if part_info['firstBloodKill']:
                specific.loc[index, 'first_blood'] += 1
            if 'firstTowerKill' in part_info and part_info['firstTowerKill']:
                specific.loc[index, 'first_tower'] += 1
        print('\t' + str(count))
        if count != 0 or count != 1:
            specific.iloc[index:index + 1, 29:] =\
                specific.iloc[index:index + 1, 29:].divide(count)
    return specific


def make_id_map():
    """
    makes map that maps champ id to champion string
    converts to dataframe
    """
    champions = pd.read_json('data/champ.json')
    m = {}
    for index, value in champions['data'].items():
        m[np.int64(value['key'])] = index
    return pd.DataFrame.from_dict(m, orient='index', columns=['c_name'])


def convert_ids(data, m):
    """
    converts champion id to string in data
    """
    data = data.merge(m, left_on='champ', right_index=True)
    return data


def remove_cols(data):
    """
    removes unneeded columns
    """
    res = data.drop(['id', 'accountId', 'puuid', 'name', 'revisionDate',
                     'summonerLevel', 'c1', 'c2', 'c3', 'c4', 'c5', 'm1',
                     'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', '0',
                     '1', '2', '3', '4', '5',
                     '6', '7', 'champ'], 1)
    res = res.dropna()
    return res


def main():
    print('file must be in the data directory')
    file_name = input('Enter file name: ')
    tier = input('Enter tier: ').upper()
    division = input('Enter division: ').upper()
    region = input('Enter region: ').upper()
    data = pd.read_csv('data/' + file_name)
    # removes strange unnamed column
    data = data.drop(data.columns[0], axis=1)
    # specific = all rows with valid icons
    # data = retrieve_icon_rows(data)
    data = add_rows(data)
    data = get_data(data)
    m = make_id_map()
    data = convert_ids(data, m)
    data = remove_cols(data)
    dest = region + '_' + tier + division + '_final' + '.csv'
    data.to_csv('data/' + dest, index=False)


if __name__ == "__main__":
    main()
