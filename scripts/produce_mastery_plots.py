import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
import numpy as np
import pandas as pd
from mastery_gather import get_roles, get_top_champs


def plot_na_roles():
    roles = ['Mage', 'Assassin', 'Marksman', 'Support', 'Fighter', 'Tank']
    all_fig, all_ax = plt.subplots(2, 3, figsize=(15, 10))
    main_fig, main_ax = plt.subplots(2, 3, figsize=(15, 10))
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
    # Is there a better way to do this?
    bc_graph = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 6, wspace=1, hspace=0.5, figure=bc_graph)
    ax1 = bc_graph.add_subplot(gs[0, 0:2])
    ax2 = bc_graph.add_subplot(gs[0, 2:4])
    ax3 = bc_graph.add_subplot(gs[0, 4:6])
    ax4 = bc_graph.add_subplot(gs[1, 1:3])
    ax5 = bc_graph.add_subplot(gs[1, 3:5])
    axes = [ax1, ax2, ax3, ax4, ax5]

    beginner_champs = ['Ahri', 'Lux', 'MasterYi', 'Darius', 'MissFortune']
    color_codes = ['fuchsia', 'cerulean', 'mustard yellow',
                   'crimson', 'pink red']
    color_codes = dict(zip(beginner_champs, color_codes))
    beginner_champs = dict(zip(beginner_champs, axes))

    leagues = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND']
    mains = pd.DataFrame()
    pop_freq = dict()

    def record_freq(col):
        col = col.sort_values(ascending=False).head(5)
        for champ in col.index:
            if champ not in pop_freq:
                pop_freq[champ] = 0
            pop_freq[champ] += 1

    for league in leagues:
        mains[league] = get_top_champs(target=(league, 'I', 'NA1'))
        mains[league] = mains[league] / mains[league].sum() * 100

    mains.apply(record_freq)
    mains.columns = [i for i in range(1, 7)]
    mains = mains.transpose()

    for champ in beginner_champs:
        sns.lineplot(data=mains[champ], ax=beginner_champs[champ],
                     color=sns.xkcd_rgb[color_codes[champ]], lw=3)
        beginner_champs[champ].set_title(champ)
        beginner_champs[champ].set_ylabel('Percentage who Play (%)')
        beginner_champs[champ].set_xlabel('Rank')
        beginner_champs[champ].set(ylim=(0, 5))
        beginner_champs[champ].set(xticks=leagues)
    bc_graph.suptitle('Players who Main Beginner Champions, By Rank (NA)',
                      fontsize=16)
    bc_graph.savefig('../img/beginner_champs_na.png')

    # return pd.Series(pop_freq).sort_values()


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
    # plot_na_roles()
    plot_na_champs()
    # plot_region_roles()


if __name__ == '__main__':
    main()
