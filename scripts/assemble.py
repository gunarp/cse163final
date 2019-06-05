import pandas as pd


def join(league, division, region, acct):
    """
    Joins MATCHES and MATCHINFO tables width-wise
    """
    front = '../data/' + league + '/' + region + '_' + \
            league + division + '_'
    back = '_' + acct + '.csv'

    summary = pd.read_csv(front + 'MATCHES' + back)
    detail = pd.read_csv(front + 'MATCHINFO' + back, header=None)

    return summary.merge(detail, left_index=True, right_index=True, sort=False)


def assemble(league, division, region, top, bot):
    """
    Assembles all data gathered for given rank on specified server into one csv
    """
    top = join(league, division, region, top)
    bot = join(league, division, region, bot)
    result = top.append(bot)
    result.to_csv('../data/' + league + '/' + region + '_' +
                  league + division + '.csv', mode='w')
    return result.shape


if __name__ == '__main__':
    print('Merging files!')
    league = input('Enter League: ').upper()
    division = input('Enter division: ').upper()
    region = input('Enter Region: ').upper()
    top = input('Enter top acct: ')
    bot = input('Enter bot acct: ')
    r = assemble(league, division, region, top, bot)
    print('Data Assembled!')
    print('Data size:', r)
