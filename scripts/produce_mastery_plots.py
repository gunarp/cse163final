import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np
import pandas as pd
from mastery_gather import get_roles, get_top_champs


def plot_na_roles():
    roles = ['Mage', 'Assassin', 'Marksman', 'Support', 'Fighter', 'Tank']
    all_fig, all_ax = plt.subplots(2, 3, figsize=(15, 10))
    main_fig, main_ax = plt.subplots(2, 3)
    league_names = np.array([['IRON', 'BRONZE', 'SILVER'],
                            ['GOLD', 'PLATINUM', 'DIAMOND']], dtype=object)
    for row in range(2):
        for col in range(3):
            league = str(league_names[row, col])
            all_roles, main_roles = get_roles(target=(league, 'I', 'NA1'))
            all_roles = pd.Series(all_roles)

            all_ax[row, col].pie(all_roles, autopct='%1.1f%%', radius=1.3,
                                 textprops=dict(color='k', size=12))
            all_ax[row, col].set_title(league + ' ' + '1', y=1.05, size=14)

            main_roles = pd.Series(main_roles)
            main_ax[row, col].pie(main_roles, autopct='%1.1f%%', radius=1.3,
                                  textprops=dict(color='k', size=12))
            main_ax[row, col].set_title(league + ' ' + '1', y=1.05, size=14)

    all_fig.legend(roles, loc='center right', title='Role',
                   bbox_to_anchor=(1, 0.5))
    all_fig.suptitle('Top Five Roles by Mastery in NA by Rank', fontsize=16)

    main_fig.legend(roles, loc='center right', title='Role',
                    bbox_to_anchor=(1, 0.5))
    main_fig.suptitle('Main Roles by Mastery in NA by Rank', fontsize=16)

    all_fig.savefig('../img/all_roles_na.png')
    main_fig.savefig('../img/main_roles_na.png')


def plot_na_champs():
    


def plot_region_roles():
    roles = ['Mage', 'Assassin', 'Marksman', 'Support', 'Fighter', 'Tank']
    all_fig, all_ax = plt.subplots(2, 3, figsize=(15, 10))
    main_fig, main_ax = plt.subplots(2, 3)
    targets = np.array([[('SILVER', 'I', 'NA1'), ('SILVER', 'I', 'KR'),
                         ('SILVER', 'I', 'EUW1')],
                       [('GOLD', 'IV', 'EUW1'), ('GOLD', 'IV', 'EUW1'),
                        ('GOLD', 'IV', 'EUW1')]], dtype=object)
    for row in range(2):
        for col in range(3):
            all_roles, main_roles = get_roles(target=targets[row, col])
            all_roles = pd.Series(all_roles)

            league, division, region = targets[row, col]

            all_ax[row, col].pie(all_roles, autopct='%1.1f%%', radius=1.3,
                                 textprops=dict(color='k', size=12))
            all_ax[row, col].set_title(region + ' ' + league + ' ' +
                                       division, y=1.05, size=14)

            main_roles = pd.Series(main_roles)
            main_ax[row, col].pie(main_roles, autopct='%1.1f%%', radius=1.3,
                                  textprops=dict(color='k', size=12))
            main_ax[row, col].set_title(region + ' ' + league + ' ' +
                                        division, y=1.05, size=14)

    all_fig.legend(roles, loc='center right', title='Role',
                   bbox_to_anchor=(1, 0.5))
    all_fig.suptitle('Average Top Five Roles by Mastery Across Regions',
                     fontsize=16)

    main_fig.legend(roles, loc='center right', title='Role',
                    bbox_to_anchor=(1, 0.5))
    main_fig.suptitle('Average Main Roles by Mastery Across Regions',
                      fontsize=16)

    all_fig.savefig('../img/all_roles_region.png')
    main_fig.savefig('../img/main_roles_region.png')


def main():
    plot_na_roles()
    plot_na_champs()
    plot_region_roles()


if __name__ == '__main__':
    main()
