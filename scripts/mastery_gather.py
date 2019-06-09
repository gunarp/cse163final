import pandas as pd
import numpy as np
import ast


def extract_feature(data, feature):
    """
    Extracts a given feature from champion mastery json string
    """
    data = ast.literal_eval(data)
    return data[feature]


def fill_params(target):
    """
    Returns a tuple containing desired dataframes.
    """
    league, division, region = target
    loc = '../data/' + league + '/' + region + '_' + league + division + '.csv'
    data = pd.read_csv(loc)
    data = data[['c' + str(i) for i in range(1, 6)]]
    data = data.dropna()
    champions = pd.read_json('../champ.json')['data']
    return(data, champions)


def get_top_champs(data=None, champions=None, target=None):
    """
    Returns a series which records the number of summoners
    in given dataset who 'main' (have most mastery points)
    any champion.
    """
    if target is not None:
        data, champions = fill_params(target)

    data = data['c1']
    c = pd.DataFrame(champions.apply(lambda x: x['key']))
    c['data'] = np.int64(c['data'])
    c = c.reset_index()

    def count(data):
        return data.value_counts()

    data = pd.DataFrame(data.apply(extract_feature, feature='championId'))
    data.columns = ['id']
    data = data.merge(c, left_on='id', right_on='data')['index']

    return data.value_counts().fillna(value=0).sort_index()


def get_roles(data=None, champions=None, target=None):
    """
    Counts how often players play champions associated with a certain role
    Returns a tuple containing two dictionaries: one containing role summaries
    across all summoners' top five champions, and another containing role
    summaries only on all summoners' top champion by champion mastery.
    """
    if target is not None:
        data, champions = fill_params(target)

    c_ids = champions.apply(lambda x: x['key'])
    c_ids = c_ids.apply(np.int64)
    c_tag = champions.apply(lambda x: x['tags'])
    c = pd.concat((c_ids, c_tag), axis=1)
    c.columns = ['id', 'tags']

    def extract_role(data):
        data = pd.DataFrame(data.apply(extract_feature, feature='championId'))
        data.columns = ['id']
        data = data.merge(c, left_on='id', right_on='id')['tags']
        return data

    data = data.apply(extract_role)
    all_roles = {}
    main_roles = {}

    def aggregate_all(col):
        def tally_up(tags):
            for tag in tags:
                if tag not in all_roles:
                    all_roles[tag] = 0
                all_roles[tag] += 1
        col.apply(tally_up)

    def aggregate_main(tags):
        for tag in tags:
            if tag not in main_roles:
                main_roles[tag] = 0
            main_roles[tag] += 1

    data.apply(aggregate_all)
    data['c1'].apply(aggregate_main)
    return (all_roles, main_roles)


def get_all(target=None):
    """
    Gathers mastery summaries for given league, division, and region.
    Mainly for personal testing.
    """
    if target is None:
        league = input('Enter League: ').upper()
        division = input('Enter Division: ').upper()
        region = input('Enter Region: ').upper()
    else:
        league, division, region = target

    loc = '../data/' + league + '/' + region + '_' + league + division + '.csv'
    data = pd.read_csv(loc)
    data = data.dropna()

    champions = pd.read_json('../champ.json')['data']

    top_champs = get_top_champs(data=data, champions=champions)
    all_roles, main_roles = get_roles(data=data, champions=champions)
    return(top_champs, all_roles, main_roles)


if __name__ == '__main__':
    get_all()
