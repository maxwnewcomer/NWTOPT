"""
Pull Trial information, and generate correlation plots and hyperparameter vs. trial plots

Requires MongoDB to be running is separate process

[usage]: python3 insights.py --ip {mongodb ip} --port {mongodb port} --key {mongodb run key} --loop
"""
# Disabling pylint snake_case warnings, import error warnings, and
# redefining out of scope warnings
#
# pylint: disable = E0401, C0103, W0621

import os
import argparse
import pandas as pd
from hyperopt.mongoexp import MongoTrials
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib as mpl

def inputHPtoArr(inputHp, NWTNUM):
    """
    Converts MongoTrials dictionary formatted hyperparameters to 1D array

    inputHp - MongoTrials Hyperparameter Dictionary
    NWTNUM - Trial NWT_Number

    returns List
    """

    # linmeth determines total hyperparm layout, using None to represent unused
    # variables for certain linmeth setting
    if inputHp['linmeth'][0] + 1 == 1:
        arr = [NWTNUM,
        inputHp['headtol'][0],
        inputHp['fluxtol'][0],
        int(inputHp['maxiterout'][0]),
        inputHp['thickfact'][0],
        inputHp['linmeth'][0] + 1,
        inputHp['iprnwt'][0],
        inputHp['ibotav'][0],
        'SPECIFIED',
        inputHp['dbdtheta'][0],
        inputHp['dbdkappa'][0],
        inputHp['dbdgamma'][0],
        inputHp['momfact'][0],
        inputHp['backflag'][0],
        int(inputHp['maxbackiter'][0]),
        inputHp['backtol'][0],
        inputHp['backreduce'][0],
        inputHp['maxitinner'][0],
        inputHp['ilumethod'][0],
        int(inputHp['levfill'][0]),
        inputHp['stoptol'][0],
        int(inputHp['msdr'][0]),
        None, None, None, None, None,
        None, None, None, None, None]
    elif inputHp['linmeth'][0] + 1 == 2:
        arr = [NWTNUM,
        inputHp['headtol'][0],
        inputHp['fluxtol'][0],
        int(inputHp['maxiterout'][0]),
        inputHp['thickfact'][0],
        inputHp['linmeth'][0] + 1,
        inputHp['iprnwt'][0],
        inputHp['ibotav'][0],
        'SPECIFIED',
        inputHp['dbdtheta'][0],
        inputHp['dbdkappa'][0],
        inputHp['dbdgamma'][0],
        inputHp['momfact'][0],
        inputHp['backflag'][0],
        int(inputHp['maxbackiter'][0]),
        inputHp['backtol'][0],
        inputHp['backreduce'][0],
        None, None, None, None, None,
        inputHp['iacl'][0],
        inputHp['norder'][0],
        int(inputHp['level'][0]),
        int(inputHp['north'][0]),
        inputHp['iredsys'][0],
        inputHp['rrctols'][0],
        inputHp['idroptol'][0],
        inputHp['epsrn'][0],
        inputHp['hclosexmd'][0],
        int(inputHp['mxiterxmd'][0])]

    return arr

def pullNWTs(ip, port, key):
    """
    Connects to MongoDB to pull NWT trials, then converts to a pandas.DataFrame object

    ip - ip of MongoDB
    port - port of MongoDB
    key - run key in MongoDB

    returns pandas.DataFrame with Hyperparameters as columns and trials as rows.

    calls:
        inputHPtoArr
    """
    print('[INFO] pulling trials')

    # Try to connect to MongoDB using specified ip:port and key
    try:
        trials = MongoTrials(f'mongo://{ip}:{port}/db/jobs', exp_key=key)
    except Exception:
        print('[ERROR] invalid ip, port, or key')
        return None

    print('[INFO] generating nwts and performance files')
    arr = []

    # iterate over each trial, convert to list using inputHPtoArr
    for i in range(len(trials.trials)):
        arr.append(inputHPtoArr(trials.trials[i].get('misc').get('vals').to_dict(), i))

    df = pd.DataFrame(arr, columns=['NWTNUM',
                                    'headtol',
                                    'fluxtol',
                                    'maxiterout',
                                    'thickfact',
                                    'linmeth',
                                    'iprnwt',
                                    'ibotav',
                                    'option',
                                    'dbdtheta',
                                    'dbdkappa',
                                    'dbdgamma',
                                    'momfact',
                                    'backflag',
                                    'maxbackiter',
                                    'backtol',
                                    'backreduce',
                                    'maxitinner',
                                    'ilumethod',
                                    'levfill',
                                    'stoptol',
                                    'msdr',
                                    'iacl',
                                    'norder',
                                    'level',
                                    'north',
                                    'iredsys',
                                    'rrctols',
                                    'idroptol',
                                    'epsrn',
                                    'hclosexmd',
                                    'mxiterxmd'])
    # get results for specified trials
    # results and hyperparams are accessed under different
    # tables, so we concat them together after pulling both
    results = []
    for i in range(len(trials.trials)):
        trial = trials.trials[i].get('result').to_dict()
        try:
            results.append([i,
                            trial['loss'],
                            trial['mass_balance'],
                            trial['sec_elapsed'],
                            trial['iterations']])
        except Exception:
            pass

    resultsDf = pd.DataFrame(results, columns=['NWT_Number',
                                            'Loss',
                                            'Mass_Balance',
                                            'Seconds_Elapased',
                                            '#_of_Iterations'])
    # combine tables
    df = pd.concat([df, resultsDf], axis=1)
    df.to_csv(os.path.join(os.getcwd(), key + '_nwts', 'param_analysis.csv'), index = False)
    return df

def heatmap(df):
    """
    Generate Hyperparamter Correlaion Heatmap from pulled hyperparamters

    df - hyperparamter pd.DataFrame generated using pullNWTs
    """

    # get correlation then use sns to plot heatmap and save the image
    corr = df.corr()
    mask = np.zeros_like(corr, dtype = np.bool)
    mask[np.triu_indices_from(mask)] = True
    plt.figure(figsize=(9,7), dpi = 1000)
    _, _ = plt.subplots(figsize = (12, 10))

    cmap = sns.diverging_palette(220, 10, as_cmap = True)

    sns.heatmap(corr, mask=mask, cmap=cmap, vmax = .3, vmin = -.3,
                center = 0, linewidths=2, cbar_kws={"shrink": .75})
    plt.savefig(fname = 'corr heatmap', dpi = 300)
    plt.show()

def cleanDf(df):
    """
    Simple clean of hyperparameter pd.DataFrame object.
    Removes failed runs and unfinished runs.

    df - hyperparameter pd.DataFrame

    returns cleaned hyperparameter pd.DataFrame
    """
    df = df[df.Mass_Balance != 999999]
    df = df[df['Loss'].notna()]
    df.drop(columns=['option'], inplace=True)
    return df

def plotCorrelations(df):
    """
    Plot loss plots in 6x6 grid for each hyperparameter, saves figure

    df - hyperparamter pd.DataFrame generated using pullNWTs
    """
    df = df[df.Loss <= 1000]
    figsize = (21, 18)
    fig = plt.figure(figsize=figsize, dpi=600)
    axes = fig.subplots(6, 6)

    col = 0
    row = 0
    for column in df.columns:
        plot = df.plot.scatter(x=column,
                                y='Loss',
                                c ='NWT_Number',
                                colormap='viridis',
                                ax=axes[col%6, row],
                                s=3,
                                colorbar=False)
        plot.set_xlabel("")
        minimum = df[column].min()
        maximum = df[column].max()
        if(minimum != 0 and maximum != 1):
            plot.set_xlim([minimum, maximum])
        axes[col%6, row].set_title(column)
        col += 1
        if col%6 == 0:
            row += 1
    plt.subplots_adjust(hspace=.4, wspace=.5)
    cax, kw = mpl.colorbar.make_axes(list(axes.flat))
    clb = plt.colorbar(axes[0][0].get_children()[0], cax=cax, **kw)
    clb.set_label('NWTNUM')
    plt.savefig(fname='corr graphs')

def plotDistributions(df):
    """
    Plot distribution plots in 6x6 grid for each hyperparameter, saves figure

    df - hyperparamter pd.DataFrame generated using pullNWTs
    """
    df = df[df.Loss <= 5]
    figsize = (21, 18)
    fig = plt.figure(figsize=figsize, dpi=600)
    axes = fig.subplots(6, 6)

    col = 0
    row = 0
    for column in df.columns:
        plot = df[[column]].plot.kde(ax=axes[col%6, row], bw_method=.1)
        plot.set_xlabel("")
        axes[col%6, row].set_title(column)
        col += 1
        if col%6 == 0:
            row += 1
    plt.subplots_adjust(hspace=.4, wspace=.5)

    plt.savefig(fname='dist graphs')

if __name__ == '__main__':
    # parse call args
    parser = argparse.ArgumentParser(description='Pull NWT analysis from DB')
    parser.add_argument('--ip', metavar='N', type=str, help='ip address of DB')
    parser.add_argument('--port', type=str, help='port of DB')
    parser.add_argument('--key', type=str, help='key of job you want to pull')
    args = parser.parse_args()

    # pull, clean, and plot
    df = pullNWTs(args.ip, args.port, args.key)
    df = cleanDf(df)
    heatmap(df)
    plotCorrelations(df)
    plotDistributions(df)
