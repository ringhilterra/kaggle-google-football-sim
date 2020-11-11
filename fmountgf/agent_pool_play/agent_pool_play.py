import pandas as pd
import numpy as np
import datetime as dt
import os
import itertools
import time
from kaggle_environments import make
from kaggle_environments.envs.football.helpers import *
from math import sqrt


EXPORT_DIR = 'pool_play_results'

AGENTS = [
    '../submit_agents/tunable-baseline-bot/submission_v6.py',
    '../submit_agents/best-open-rules-bot/submission_v2.py',
    '../submit_agents/gfootball-with-memory-patterns/submission_v15.py',
    '../submit_agents/gfootball-with-memory-patterns/submission_v32.py',
    '../submit_agents/gfootball-with-memory-patterns/submission_v43.py',
    '../submit_agents/gfootball-with-memory-patterns/submission_v55.py',
    '../submit_agents/maraud_wingers/submission_v1.py'
]

NUM_ROUNDS = 10
EPISODE_STEPS = 3000
SCENARIO_NAME = '11_vs_11_kaggle'


def run_pool_play(scenario_name, episode_steps, num_rounds, agents, export_dir, write_file=False):
    print('run pool play scenario: {0}'.format(scenario_name))
    start_time = time.time()
    
    agents_dirs = agents
    
    env_config = {
        "save_video": False,
        "scenario_name": scenario_name,
        "running_in_notebook": False,
        "episodeSteps": episode_steps
    }
    
    env = make("football", configuration=env_config, debug=False)
    
    
    df_list = []

    for pool_play_round in range(num_rounds):
        for agent1 in agents_dirs:
            for agent2 in agents_dirs:
                print(agent1, agent2)
                env.reset()
                output = env.run([agent1, agent2])

                final_output = output[-1]
                left_agent_foutput = final_output[0]
                right_agent_foutput = final_output[1]
                left_reward = left_agent_foutput['reward']
                right_reward = right_agent_foutput['reward']
                left_status = left_agent_foutput['status']
                right_status = right_agent_foutput['status']

                left_score = output[-1][0]['observation']['players_raw'][0]['score'][0]
                right_score = output[-1][0]['observation']['players_raw'][0]['score'][1]

                adf = pd.DataFrame()
                adf['scenario'] = [scenario_name]
                adf['round'] = [pool_play_round]
                adf['left_agent'] = [agent1]
                adf['right_agent'] = [agent2]
                adf['left_score'] = [left_score]
                adf['right_score'] = [right_score]
                adf['left_reward'] = [left_reward]
                adf['right_reward'] = [right_reward]
                adf['left_status'] = [left_status]
                adf['right_status'] = [right_status]

                df_list.append(adf)

        pool_play_round +=1
        
    #final dataframe with results    
    result_df = pd.concat(df_list)
    
    # get scoreboard result dataframe
    score_df = get_scoreboard(result_df)
    # add some final columns
    score_df['scenario_name'] = scenario_name
    score_df = score_df[['scenario_name','agent', 'games_played', 'num_wins', 'num_losses', 'num_ties',
       'goals_for', 'goals_against', 'num_points']]
    
    # write out results to file if flag set
    if write_file:
        # if export_dir does not exist then create it
        if export_dir not in os.listdir('.'):
            print('{0} directory does not exist, creating'.format(export_dir) )
            os.mkdir(export_dir)
        
        # make export directory w/ timestamp of runs
        curr_datetime = dt.datetime.now()
        curr_time = curr_datetime.strftime('%m-%d-%Y-%H-%M-%S')
        export_fdir = export_dir + '/' +  curr_time
        os.mkdir(export_fdir)

        # write out results
        export_result_file = export_fdir + '/results.csv'
        result_df.to_csv(export_result_file, index=False)
        print('results written out to {0}'.format(export_result_file))
        
        # write out score df
        export_score_file = export_fdir + '/scoreboard.csv'
        score_df.to_csv(export_score_file, index=False)

        # write out config
        config_df = pd.DataFrame(env_config.items())
        config_df = config_df.append([['num_rounds', num_rounds]])
        config_df.to_csv(export_fdir + '/config.csv', index=False)

        end_time = round((time.time() - start_time), 2)
        print("complete: --- %s seconds ---" % end_time)
    
    return result_df, score_df


def get_scoreboard_from_file(result_file):
    rdf = pd.read_csv(result_file)
    score_df = get_scoreboard(rdf)
    return score_df


def get_scoreboard(rdf):
    # get only cases where valid statuses
    rdf = rdf[rdf['right_status'] == 'DONE']
    rdf = rdf[rdf['left_status'] == 'DONE']

    agents = list(set(list(rdf.left_agent.unique()) + list(rdf.right_agent.unique())))
    
    result_list = []

    for agent in agents:
        left_df = rdf[rdf.left_agent == agent].reset_index(drop=True)

        # calculate num_wins, num_losses, num_ties
        left_df['num_wins'] = np.where(left_df['left_score'] > left_df['right_score'], 1, 0)
        left_df['num_losses'] = np.where(left_df['left_score'] < left_df['right_score'], 1, 0)
        left_df['num_ties'] = np.where(left_df['left_score'] == left_df['right_score'], 1, 0)

        games_played = len(left_df)
        goals_for = left_df.left_score.sum()
        goals_against = left_df.right_score.sum()
        num_wins = left_df.num_wins.sum()
        num_losses = left_df.num_losses.sum()
        num_ties = left_df.num_ties.sum()

        right_df = rdf[rdf.right_agent == agent].reset_index(drop=True)

        # calculate num_wins, num_losses, num_ties
        right_df['num_wins'] = np.where(right_df['right_score'] > right_df['left_score'], 1, 0)
        right_df['num_losses'] = np.where(right_df['right_score'] < right_df['left_score'], 1, 0)
        right_df['num_ties'] = np.where(right_df['right_score'] == right_df['left_score'], 1, 0)

        games_played = games_played + len(right_df)
        goals_for = goals_for + right_df.right_score.sum()
        goals_against = goals_against + right_df.left_score.sum()
        num_wins = num_wins + right_df.num_wins.sum()
        num_losses = num_losses + right_df.num_losses.sum()
        num_ties = num_ties + right_df.num_ties.sum()

        result_list.append([agent, games_played, num_wins, num_losses, num_ties, goals_for, goals_against])

    fdf = pd.DataFrame(result_list, columns = ['agent', 'games_played', 'num_wins', 'num_losses', 'num_ties',
                                               'goals_for', 'goals_against'])

    fdf['num_points'] = fdf['num_wins']*3 + fdf['num_ties']*1

    fdf = fdf.sort_values('num_points', ascending=False)
    
    return fdf


# START HERE
result_df, score_df = run_pool_play(SCENARIO_NAME, EPISODE_STEPS, NUM_ROUNDS, AGENTS, EXPORT_DIR, write_file=True)