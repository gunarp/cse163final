# Constructs several ML models using icon data
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")


def clean_data(data):
    """
    Appends all of the icon data from division I of every tier
    Only rows with valid icons are included
    """
    purple = data['profileIconId'] == 4087
    red = data['profileIconId'] == 4086
    blue = data['profileIconId'] == 4089
    green = data['profileIconId'] == 4088

    specific = data[purple | red | blue | green]
    specific = specific.reset_index(drop=True)
    return specific


def model_DTC(data):
    """
    Constructs DecisionTreeClassifier Model
    """
    y = data['profileIconId']
    X = data.loc[:, data.columns != 'profileIconId']
    X = pd.get_dummies(X)
    model = DecisionTreeClassifier()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model.fit(X_train, y_train)
    print('Decision Tree:', accuracy_score(y_test, model.predict(X_test)))


def model_RF(data):
    """
    Constructs random forest classifier
    """
    y = data['profileIconId']
    X = data.loc[:, data.columns != 'profileIconId']
    X = pd.get_dummies(X)
    RF = RandomForestClassifier(n_estimators=100, max_depth=2)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    RF.fit(X_train, y_train)
    print('Random Forest:', accuracy_score(y_test, RF.predict(X_test)))


def model_NN(data):
    """
    Constructs Neural Network classifier
    """
    y = data['profileIconId']
    X = data.loc[:, data.columns != 'profileIconId']
    X = pd.get_dummies(X)
    NN = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(50, 10))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    NN.fit(X_train, y_train)
    print('Neural Network:', accuracy_score(y_test, NN.predict(X_test)))


def make_graph2(data):
    """
    Constructs a graph that displays champion mains for
    each house
    """
    purple = data[data['profileIconId'] == 4087]
    red = data[data['profileIconId'] == 4086]
    blue = data[data['profileIconId'] == 4089]
    green = data[data['profileIconId'] == 4088]

    fig, [[ax1, ax2], [ax3, ax4]] =\
        matplotlib.pyplot.subplots(2, figsize=(20, 10), ncols=2)
    red = red.groupby('c_name').size().reset_index(name='counts')
    red = red[red['counts'] > 5]
    purple = purple.groupby('c_name').size().reset_index(name='counts')
    purple = purple[purple['counts'] > 5]
    blue = blue.groupby('c_name').size().reset_index(name='counts')
    blue = blue[blue['counts'] > 5]
    green = green.groupby('c_name').size().reset_index(name='counts')
    green = green[green['counts'] > 5]

    red.plot(kind='pie', labels=red['c_name'], y='counts',
             autopct='%1.1f%%', legend=False, ax=ax1)
    ax1.set_title('Faceless (Red)')
    purple.plot(kind='pie', labels=purple['c_name'], y='counts',
                autopct='%1.1f%%', legend=False, ax=ax2)
    ax2.set_title('Warband (Purple)')
    green.plot(kind='pie', labels=green['c_name'], y='counts',
               autopct='%1.1f%%', legend=False, ax=ax3)
    ax3.set_title('United (Green)')
    blue.plot(kind='pie', labels=blue['c_name'], y='counts',
              autopct='%1.1f%%', legend=False, ax=ax4)
    ax4.set_title('Council (Blue)')
    matplotlib.pyplot.savefig('champion_vs_house.png')


def main():
    file_name = input('File name: ')
    data = pd.read_csv('data/' + file_name)
    data = clean_data(data)
    # model_DTC(data)
    # model_RF(data)
    # model_NN(data)
    # make_graph1(data)
    make_graph2(data)


if __name__ == '__main__':
    main()
