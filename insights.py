# Insights
import os
import pandas as pd
from hyperopt import Trials
from hyperopt.mongoexp import MongoTrials
import argparse
import subprocess
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib as mpl


def inputHp2df(inputHp, NWTNUM, args):
    array = []
    if inputHp['linmeth'][0] + 1 == 1:
        arr = [NWTNUM, inputHp['headtol'][0], inputHp['fluxtol'][0], int(inputHp['maxiterout'][0]),
        inputHp['thickfact'][0], inputHp['linmeth'][0] + 1, inputHp['iprnwt'][0], inputHp['ibotav'][0], 'SPECIFIED', inputHp['dbdtheta'][0],
        inputHp['dbdkappa'][0], inputHp['dbdgamma'][0], inputHp['momfact'][0], inputHp['backflag'][0], int(inputHp['maxbackiter'][0]), inputHp['backtol'][0],
        inputHp['backreduce'][0], inputHp['maxitinner'][0], inputHp['ilumethod'][0], int(inputHp['levfill'][0]), inputHp['stoptol'][0], int(inputHp['msdr'][0]),
        None, None, None, None, None, None, None, None, None, None]


    elif inputHp['linmeth'][0] + 1 == 2:
        arr = [NWTNUM, inputHp['headtol'][0], inputHp['fluxtol'][0], int(inputHp['maxiterout'][0]),
        inputHp['thickfact'][0], inputHp['linmeth'][0] + 1, inputHp['iprnwt'][0], inputHp['ibotav'][0], 'SPECIFIED', inputHp['dbdtheta'][0],
        inputHp['dbdkappa'][0], inputHp['dbdgamma'][0], inputHp['momfact'][0], inputHp['backflag'][0], int(inputHp['maxbackiter'][0]), inputHp['backtol'][0],
        inputHp['backreduce'][0], None, None, None, None, None, inputHp['iacl'][0], inputHp['norder'][0], int(inputHp['level'][0]), int(inputHp['north'][0]), inputHp['iredsys'][0], inputHp['rrctols'][0],
        inputHp['idroptol'][0], inputHp['epsrn'][0], inputHp['hclosexmd'][0], int(inputHp['mxiterxmd'][0])]
    return arr

def pullNWTs(ip, port, key, args):
    print('[INFO] pulling trials')
    try:
        trials = MongoTrials('mongo://' + ip + ':' + port + '/db/jobs', exp_key=key)
    except:
        print('[ERROR] invalid ip, port, or key')
        return
    print('[INFO] generating nwts and performance files')
    arr = []
    for i in range(len(trials.trials)):
        arr.append(inputHp2df(trials.trials[i].get('misc').get('vals').to_dict(), i, args))
    df = pd.DataFrame(arr, columns=['NWTNUM', 'headtol', 'fluxtol', 'maxiterout', 'thickfact', 'linmeth', 'iprnwt', 'ibotav', 'option', 'dbdtheta', 'dbdkappa', 'dbdgamma', 'momfact', 'backflag',
    'maxbackiter', 'backtol', 'backreduce', 'maxitinner', 'ilumethod', 'levfill', 'stoptol', 'msdr', 'iacl', 'norder', 'level', 'north', 'iredsys', 'rrctols', 'idroptol', 'epsrn', 'hclosexmd', 'mxiterxmd'])
    results = []
    for i in range(len(trials.trials)):
        trial = trials.trials[i].get('result').to_dict()
        try:
            results.append([i, trial['loss'], trial['mass_balance'], trial['sec_elapsed'], trial['iterations']])
        except:
            pass
    resultsDf = pd.DataFrame(results, columns=['NWT_Number', 'Loss', 'Mass_Balance', 'Seconds_Elapased', '#_of_Iterations'])
    df = pd.concat([df, resultsDf], axis=1)
    print(df)
    df.to_csv(os.path.join(os.getcwd(), args.key + '_nwts', 'param_analysis.csv'), index = False)
    return df

def heatmap(df):
    corr = df.corr()
    mask = np.zeros_like(corr, dtype = np.bool)
    mask[np.triu_indices_from(mask)] = True
    plt.figure(figsize=(9,7), dpi = 1000)
    f, ax = plt.subplots(figsize = (12, 10))

    cmap = sns.diverging_palette(220, 10, as_cmap = True)

    sns.heatmap(corr, mask=mask, cmap=cmap, vmax = .3, vmin = -.3, center = 0, linewidths=2, cbar_kws={"shrink": .75})
    plt.savefig(fname = 'corr heatmap', dpi = 300)
    plt.show()

def cleanDf(df):
    df = df[df.Mass_Balance != 999999]
    df = df[df['Loss'].notna()]
    df.drop(columns=['option'], inplace=True)
    return df

def plotCorrelations(df):
    df = removeHighLoss(df, 1000)
    figsize = (21, 18)
    fig = plt.figure(figsize=figsize, dpi=600)
    axes = fig.subplots(6, 6)

    col = 0
    row = 0
    for column in df.columns:
        plot = df.plot.scatter(x=column, y='Loss', c ='NWT_Number', colormap='viridis', ax=axes[col%6, row], s=3, colorbar=False)
        plot.set_xlabel("")
        min = df[column].min()
        max = df[column].max()
        if(min != 0 and max != 1):
            plot.set_xlim([min, max])
        axes[col%6, row].set_title(column)
        col += 1
        if col%6 == 0:
            row += 1
    plt.subplots_adjust(hspace=.4, wspace=.5)
    cax,kw = mpl.colorbar.make_axes([ax for ax in axes.flat])
    clb = plt.colorbar(axes[0][0].get_children()[0], cax=cax, **kw)
    clb.set_label('NWTNUM')

    plt.savefig(fname='corr graphs')

def plotDistributions(df):
    df = removeHighLoss(df, 5)
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

def removeHighLoss(df, limit):
    df = df[df.Loss <= limit]
    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pull NWT analysis from DB')
    parser.add_argument('--ip', metavar='N', type=str, help='ip address of DB')
    parser.add_argument('--port', type=str, help='port of DB')
    parser.add_argument('--key', type=str, help='key of job you want to pull')
    parser.add_argument('--loop', type=bool, required=False, default=False)
    args = parser.parse_args()
    cwd = os.getcwd()
    db = subprocess.Popen(cwd + '/mongodb/bin/mongod --dbpath ' + cwd + '/mongodb/db --bind_ip ' + args.ip + ' --port '+ args.port + ' --quiet > db_output.txt', shell = True)
    df = pullNWTs(args.ip, args.port, args.key, args)
    df = cleanDf(df)
    heatmap(df)
    #plotCorrelations(df)
    plotDistributions(df)
