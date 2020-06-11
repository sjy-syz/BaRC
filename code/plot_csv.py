import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os



LEGEND = {'adaptiveTbrs': 'Linearly increase T from 0.1 to 0.5 over 20 iterations',
          'adaptiveTbrs10':'Linearly increase T from 0.1 to 0.5 over 10 iterations',
          'adapt':'Linearly increase T from 0.1 to 0.5 over 20 iterations',
          'fixT': 'T=0.1',
          'heuristc':'Heuristic',
          'heu':'Heuristic',
          'ppo':'PPO only'}
labels = ['adapt','fixT', 'heu', 'ppo']
def group():

    data = {}
    results = {}
    for label in labels:
        data[label] = []
    RUN_DIR = os.path.join(os.getcwd(), 'runs')
    for dir in os.listdir(RUN_DIR):
        dir_path = os.path.join(RUN_DIR, dir)
        if os.path.isdir(dir_path):
            file_path = os.path.join(dir_path, 'data', 'data_backreach.csv')
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
            else:
                file_path = os.path.join(dir_path, 'data', 'data_ppo_only.csv')
            df = pd.read_csv(file_path)
            df['timestamp'] -= df['timestamp'][1]
            # df = df.fillna(0.0)

            for label in labels:
                if label in file_path:
                    print(file_path)
                    data[label].append(df)
                    break
    for label in labels:
        df1 = data[label][0]
        df2 = data[label][1]
        df = pd.concat([df1, df2], sort=False)
        for i, idf in enumerate(data[label]):
            if i > 1:
                df = pd.concat([df, idf], sort=False)
        results[label] = df
    return results


    pass


def plt_over_time(dir_path, ax):
    file_path = os.path.join(dir_path, 'data', 'data_backreach.csv')
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        file_path = os.path.join(dir_path, 'data', 'data_ppo_only.csv')
    df = pd.read_csv(file_path)
    df['timestamp'] -= df['timestamp'][1]
    sns.lineplot(x='timestamp', y='overall_reward', data=df, ax=ax)#,label=LEGEND[file_path.split('_')[1]])
    # df['overall_area'].plperfot()

    return df

def plt_over_iter(dir_path, ax):
    file_path = os.path.join(dir_path, 'data', 'data_backreach.csv')
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        file_path = os.path.join(dir_path, 'data', 'data_ppo_only.csv')
    df = pd.read_csv(file_path)
    sns.lineplot(x='overall_iter', y='overall_perf', data=df, ax=ax)#, label=LEGEND[file_path.split('_')[1]])
    # df['overall_area'].plot()

    return df

def plot_all():
    fig, ax = plt.subplots()
    results = {}
    results = group()
    for label in labels:
        sns.lineplot(x='overall_iter', y='overall_perf', data=results[label], ax=ax, label=LEGEND[label])
    plt.xlabel('Algorithm Iteration')
    plt.xlim([0, 20])
    plt.ylabel('Success starts (%)')
    fig.savefig('Overall_area_iter.png')
    plt.show()


    fig, ax = plt.subplots()
    c = [sns.xkcd_rgb["medium blue"], sns.xkcd_rgb["orange"], sns.xkcd_rgb["medium green"]]
    for i,label in enumerate(labels):
        sns.lineplot(x=results[label].index, y='overall_perf', data=results[label], ax=ax, label=LEGEND[label])
        # if i < 3:
        #     plt.axvline(x=results[label]['timestamp'].max(), c = c[i], linestyle='dashed')
    plt.xlabel('Time Stamp')

    plt.ylabel('Success starts (%)')
    fig.savefig('Overall_area.png')
    plt.show()

    # fig, ax = plt.subplots()
    # results = group()
    # for label in labels:
    #     sns.lineplot(x=results[label].index, y='ppo_perf', data=results[label], ax=ax, label=label)
    # plt.xlabel('PPO performance')
    # plt.ylabel('Success starts (%)')
    # fig.savefig('Overall_.png')
    # plt.show()

    fig, ax = plt.subplots()

    for label in labels:
        sns.lineplot(x=results[label].index, y='ppo_rews', data=results[label], ax=ax, label=LEGEND[label])
    plt.xlabel('PPO Iteration')
    plt.xlim([0, 400])
    plt.ylabel('PPO rewards')
    fig.savefig('ppo_rew.png')
    plt.show()


    # RUN_DIR = os.path.join(os.getcwd(), 'runs')
    # for dir in os.listdir(RUN_DIR):
    #     dir_path = os.path.join(RUN_DIR, dir)
    #     if os.path.isdir(dir_path):
    #         dataf = plt_over_time(dir_path, ax)
    # plt.xlabel('Time')
    # plt.xlim([0, 8000])
    # plt.ylabel('Success starts (%)')
    # fig.savefig('Overall_area.png')
    # plt.show()
    #
    # fig, ax = plt.subplots()
    # RUN_DIR = os.path.join(os.getcwd(), 'runs')
    # for dir in os.listdir(RUN_DIR):
    #     dir_path = os.path.join(RUN_DIR, dir)
    #     if os.path.isdir(dir_path):
    #         dataf = plt_over_iter(dir_path, ax)
    # plt.xlabel('Algorithm Iteration')
    # plt.ylabel('Success starts (%)')
    # fig.savefig('Overall_area_iter.png')
    # plt.show()





if __name__ == '__main__':
    fig, ax = plt.subplots()
    plt_over_iter('/home/jingjia16', ax)
    plt.show()

    


    pass