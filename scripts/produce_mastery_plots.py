import seaborn as sns
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image
from io import BytesIO
from mastery_gather import get_roles, get_top_champs

"""
produce_mastery_plots creates the plots used in our analysis of what champions
and roles seem to do best in ranked play.
There is a lot we could improve on in our analysis, as looking only at champion
masteries strongly favors champions who have been out for longer (as a high
mastery score can be built simply by playing a champion a lot).
"""


def plot_na_roles():
    """
    Creates two figures containing role distributions across all ranks in NA
    """
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
                                 textprops=dict(color='k', size=14))
            all_ax[row, col].set_title(league + ' ' + '1', y=1.05, size=16)

            main_roles = pd.Series(main_roles)
            main_ax[row, col].pie(main_roles, autopct='%1.1f%%', radius=1.3,
                                  textprops=dict(color='k', size=14))
            main_ax[row, col].set_title(league + ' ' + '1', y=1.05, size=16)

    all_fig.legend(roles, loc='center right', title='Role',
                   bbox_to_anchor=(1, 0.5))
    all_fig.suptitle('Top Five Roles by Mastery in NA by Rank', fontsize=20)

    main_fig.legend(roles, loc='center right', title='Role',
                    bbox_to_anchor=(1, 0.5))
    main_fig.suptitle('Main Roles by Mastery in NA by Rank', fontsize=20)

    all_fig.savefig('../img/all_roles_na.png')
    main_fig.savefig('../img/main_roles_na.png')


def produce_champ_rank_plot(mains, leagues):
    """
    Helper function for plot_na_champs. Actually creates the plot.
    """
    # Is there a better way to do this?
    bc_graph = plt.figure(figsize=(22.5, 15))
    gs = GridSpec(2, 6, wspace=1, hspace=0.2, figure=bc_graph)
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
    axes = dict(zip(beginner_champs, axes))

    for champ in beginner_champs:
        sns.lineplot(data=mains[champ], ax=axes[champ],
                     color=sns.xkcd_rgb[color_codes[champ]], lw=3)
        axes[champ].set_title(champ, size=16)
        axes[champ].set_ylabel('Percentage who Play (%)')
        axes[champ].set_xlabel('Rank')
        axes[champ].set(ylim=(0, 5))
        axes[champ].set(xticks=[i for i in range(1, len(leagues) + 1)])
        axes[champ].set(xticklabels=leagues)
    bc_graph.suptitle('Players who Main Beginner Champions, By Rank (NA)',
                      fontsize=20)
    bc_graph.savefig('../img/beginner_champs_na.png')


def produce_champ_pop_plot(pop_freq, purpose, dest):
    """
    Helper function for plot_na_champs and plot_region_champs.
    Actually creates the figure
    """
    pop_freq = pd.DataFrame.from_dict(pop_freq, orient='index').reset_index()
    pop_freq.columns = ['champ', 'freq']
    pop_freq = pop_freq.groupby('freq')['champ'].apply(list)
    pop_freq = pop_freq.sort_index(ascending=False).head(3)
    ncol = pop_freq.apply(len).max()
    nrow = pop_freq.shape[0]

    pop_champs = plt.figure(figsize=(ncol*3, 9))
    gs = GridSpec(nrow, ncol, wspace=0.5)
    for row, li in enumerate(pop_freq):
        for col, champion in enumerate(li):
            ax = pop_champs.add_subplot(gs[row, col])
            r = requests.get('http://ddragon.leagueoflegends.com' +
                             '/cdn/9.10.1/img/champion/' + champion + '.png')
            ax.imshow(Image.open(BytesIO(r.content)), interpolation='none')
            ax.set_title(champion, size=16)
            ax.set_xticks([])
            ax.set_yticks([])
            if col == 0:
                ax.set_ylabel(pop_freq.index[row], rotation=0,
                              labelpad=25, size=20)
    pop_champs.suptitle('Cumulative High Champion\nPopularity for ' + purpose,
                        size=20)
    pop_champs.savefig('../img/pop_champs_' + dest + '.png')


def produce_top_bot_plot(mains):
    """
    Helper function for plot_na_champs, actually produces a plot
    """
    avg = mains.mean(axis=1)
    top_bot, axes = plt.subplots(2, 5, figsize=(15, 6))

    bot = avg.sort_values().head(5)
    top = avg.sort_values(ascending=False).head(5)
    to_plot = (top, bot)
    for row, li in enumerate(to_plot):
        for col, champ in enumerate(li.index):
            ax = axes[row, col]
            r = requests.get('http://ddragon.leagueoflegends.com' +
                             '/cdn/9.10.1/img/champion/' + champ + '.png')
            f = int(li[champ] * 100) / 100
            ax.imshow(Image.open(BytesIO(r.content)), interpolation='none')
            ax.set_title(champ + ', ' + str(f) + '%', size=16)
            ax.set_xticks([])
            ax.set_yticks([])
    axes[0, 0].set_ylabel('Top 5', rotation=0, labelpad=50, size=20)
    axes[1, 0].set_ylabel('Bottom 5', rotation=0, labelpad=50, size=20)

    top_bot.suptitle('Over/Underrepresented Champions across all ranks in NA',
                     size=20)
    top_bot.savefig('../img/top_bot_na.png')


def plot_na_champs():
    """
    Saves three figures as images.
    First figure shows a list of the most and least popular champions
    among all ranks in NA by percent of players who main them.
    Second figure shows the proportion of players who main
    beginner champions (who can be obtained for free after
    finishing the game tutorial) in each rank.
    Third figure shows a list of the most popular champions
    among all ranks in NA. Popularity was determined by the number
    of times the champion was among the top among the top five most mained
    champions by mastery in each rank.
    """
    leagues = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND']
    mains = pd.DataFrame()
    pop_freq = dict()

    for league in leagues:
        mains[league] = get_top_champs(target=(league, 'I', 'NA1'))
        mains[league] = mains[league] / mains[league].sum() * 100

    def record_pop_freq(col):
        col = col.sort_values(ascending=False).head(5)
        for champ in col.index:
            if champ not in pop_freq:
                pop_freq[champ] = 0
            pop_freq[champ] += 1

    mains.apply(record_pop_freq)
    mains.columns = [i for i in range(1, len(leagues) + 1)]

    produce_top_bot_plot(mains)

    mains = mains.transpose()
    produce_champ_rank_plot(mains, leagues)

    produce_champ_pop_plot(pop_freq, 'All Ranks in NA', 'na')


def plot_region_roles():
    roles = ['Mage', 'Assassin', 'Marksman', 'Support', 'Fighter', 'Tank']
    all_fig, all_ax = plt.subplots(2, 3, figsize=(15, 10))
    main_fig, main_ax = plt.subplots(2, 3, figsize=(15, 10))
    targets = np.array([[('SILVER', 'I', 'NA1'), ('SILVER', 'I', 'KR'),
                         ('SILVER', 'I', 'EUW1')],
                       [('GOLD', 'IV', 'NA1'), ('GOLD', 'IV', 'KR'),
                        ('GOLD', 'IV', 'EUW1')]], dtype=object)
    for row in range(2):
        for col in range(3):
            all_roles, main_roles = get_roles(target=targets[row, col])
            all_roles = pd.Series(all_roles)

            league, division, region = targets[row, col]

            all_ax[row, col].pie(all_roles, autopct='%1.1f%%', radius=1.3,
                                 textprops=dict(color='k', size=14))
            all_ax[row, col].set_title(region + ' ' + league + ' ' +
                                       division, y=1.05, size=16)

            main_roles = pd.Series(main_roles)
            main_ax[row, col].pie(main_roles, autopct='%1.1f%%', radius=1.3,
                                  textprops=dict(color='k', size=14))
            main_ax[row, col].set_title(region + ' ' + league + ' ' +
                                        division, y=1.05, size=16)

    all_fig.legend(roles, loc='center right', title='Role',
                   bbox_to_anchor=(1, 0.5))
    all_fig.suptitle('Average Top Five Roles by Mastery Across Regions',
                     fontsize=20)

    main_fig.legend(roles, loc='center right', title='Role',
                    bbox_to_anchor=(1, 0.5))
    main_fig.suptitle('Average Main Roles by Mastery Across Regions',
                      fontsize=20)

    all_fig.savefig('../img/all_roles_region.png')
    main_fig.savefig('../img/main_roles_region.png')


def plot_region_champs():
    """
    Saves three figures as images.
    First figure shows a list of the most popular champions
    among 'average' players (SILVER I and GOLD IV) in NA.
    Popularity was determined by the number of times the champion was
    among the top among the top five most mained champions by mastery in
    each examined rank.
    The second and third figures are the same, but for KR and EUW.
    """
    na = [('GOLD', 'IV', 'NA1'), ('SILVER', 'I', 'NA1')]
    kr = [('GOLD', 'IV', 'KR'), ('SILVER', 'I', 'KR')]
    euw = [('GOLD', 'IV', 'EUW1'), ('SILVER', 'I', 'EUW1')]
    regions = [('NA', na), ('KR', kr), ('EUW', euw)]

    for region in regions:
        mains = pd.DataFrame()
        pop_freq = dict()
        targets = region[1]

        for target in targets:
            league = target[0]
            mains[league] = get_top_champs(target=target)

        def record_pop_freq(col):
            col = col.sort_values(ascending=False).head(5)
            for champ in col.index:
                if champ not in pop_freq:
                    pop_freq[champ] = 0
                pop_freq[champ] += 1

        mains.apply(record_pop_freq)

        produce_champ_pop_plot(pop_freq, 'Average Ranks in ' + region[0],
                               region[0].lower() + '_avg')


def main():
    # plot_na_roles()
    plot_na_champs()
    # plot_region_roles()
    # plot_region_champs()


if __name__ == '__main__':
    main()
