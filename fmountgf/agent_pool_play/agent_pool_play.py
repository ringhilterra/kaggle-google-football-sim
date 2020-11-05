import pandas as pd
import datetime as dt
import os
import itertools
import time
from kaggle_environments import make
from kaggle_environments.envs.football.helpers import *
from math import sqrt

AGENTS_DIR = '../submit_agents/'
EXPORT_DIR = 'pool_play_results/'
NUM_POOL_PLAYS = 10

agents = [
    'tunable-baseline-bot/submission_v6.py',
    'best-open-rules-bot/submission_v2.py',
    'gfootball-with-memory-patterns/submission_v15.py',
    'gfootball-with-memory-patterns/submission_v28.py',
    'gfootball-with-memory-patterns/submission_v32.py',
]

env_config = {
    "save_video": False,
    "scenario_name": "11_vs_11_kaggle",
    "running_in_notebook": True,
    "episodeSteps": 3000
}


def run_pool_play():
    print('run start')
    start_time = time.time()
    
    agents_dirs = [AGENTS_DIR + x for x in agents]
    all_agents_dirs_combo = list(itertools.combinations(agents_dirs,2))
    
    env = make("football", configuration=env_config, debug=False)
    
    
    df_list = []

    for pool_play_round in range(NUM_POOL_PLAYS):
        for agent1, agent2 in all_agents_dirs_combo:
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
            adf['round'] = [pool_play_round]
            adf['left_agent'] = [agent1.replace(AGENTS_DIR, '')]
            adf['right_agent'] = [agent2.replace(AGENTS_DIR, '')]
            adf['left_score'] = [left_score]
            adf['right_score'] = [right_score]
            adf['left_reward'] = [left_reward]
            adf['right_reward'] = [right_reward]
            adf['left_status'] = [left_status]
            adf['right_status'] = [right_status]

            df_list.append(adf)

        pool_play_round +=1
        
    
    fdf = pd.concat(df_list)
    
    # make export directory w/ timestamp of runs
    curr_datetime = dt.datetime.now()
    curr_time = curr_datetime.strftime('%d-%m-%Y-%H-%M-%S')
    export_fdir = EXPORT_DIR + curr_time
    os.mkdir(export_fdir)
    
    # write out results
    fdf.to_csv(export_fdir + '/results.csv', index=False)
    
    
    # write out config
    config_df = pd.DataFrame(env_config.items())
    config_df = config_df.append([['num_pool_plays', NUM_POOL_PLAYS]])
    config_df.to_csv(export_fdir + '/config.csv', index=False)
    
    end_time = round((time.time() - start_time), 2)
    print("complete: --- %s seconds ---" % end_time)
    
    return


# START HERE
run_pool_play()