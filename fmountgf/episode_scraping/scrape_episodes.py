import pandas as pd
import numpy as np
import os
import requests
import json
import datetime as dt
import time


base_url = "https://www.kaggle.com/requests/EpisodeService/"
get_url = base_url + "GetEpisodeReplay"
list_url = base_url + "ListEpisodes"

def getTeamEpisodes(team_id):
    r = requests.post(list_url, json = {"teamId":  int(team_id)})
    rj = r.json()

    # update teams list
#     global teams_df
#     teams_df_new = pd.DataFrame(rj['result']['teams'])
    
#     if len(teams_df.columns) == len(teams_df_new.columns) and (teams_df.columns == teams_df_new.columns).all():
#         teams_df = pd.concat( (teams_df, teams_df_new.loc[[c for c in teams_df_new.index if c not in teams_df.index]] ) )
#         teams_df.sort_values('publicLeaderboardRank', inplace = True)
#     else:
#         print('teams dataframe did not match')
    
    # make df
    team_episodes = pd.DataFrame(rj['result']['episodes'])
    team_episodes['avg_score'] = -1;
    
    for i in range(len(team_episodes)):
        agents = team_episodes['agents'].loc[i]
        agent_scores = [a['updatedScore'] for a in agents if a['updatedScore'] is not None]
        team_episodes.loc[i, 'submissionId'] = [a['submissionId'] for a in agents if a['submission']['teamId'] == team_id][0]
        team_episodes.loc[i, 'updatedScore'] = [a['updatedScore'] for a in agents if a['submission']['teamId'] == team_id][0]
        
        if len(agent_scores) > 0:
            team_episodes.loc[i, 'avg_score'] = np.mean(agent_scores)

    for sub_id in team_episodes['submissionId'].unique():
        sub_rows = team_episodes[ team_episodes['submissionId'] == sub_id ]
        max_time = max( [r['seconds'] for r in sub_rows['endTime']] )
        final_score = max( [r['updatedScore'] for r_idx, (r_index, r) in enumerate(sub_rows.iterrows())
                                if r['endTime']['seconds'] == max_time] )

        team_episodes.loc[sub_rows.index, 'final_score'] = final_score
        
    team_episodes.sort_values('avg_score', ascending = False, inplace=True)
    return rj, team_episodes


def saveEpisode(epid, rj):
    # request
    re = requests.post(get_url, json = {"EpisodeId": int(epid)})
        
    # save replay
    with open('{}.json'.format(epid), 'w') as f:
        f.write(re.json()['result']['replay'])

    # save episode info
    with open('{}_info.json'.format(epid), 'w') as f:
        json.dump([r for r in rj['result']['episodes'] if r['id']==epid][0], f)


def saveEpisode_v2(epid, output_dir='episodes_dl/'):
    print('saveEpisode_v2: {0}'.format(epid))
    # request
    re = requests.post(get_url, json = {"EpisodeId": int(epid)})
        
    # save replay
    with open(output_dir + '{}.json'.format(epid), 'w') as f:
        f.write(re.json()['result']['replay'])


def scrape_save_team_top_submit(team_id, submission_id, min_eps_id=0, output_dir='episodes_dl/'):
    
    print('run start')
    start_time = time.time()
    
    
    # make export directory w/ timestamp of runs
    curr_datetime = dt.datetime.now()
    curr_time = curr_datetime.strftime('%m-%d-%Y-%H-%M-%S')
    output_dir = output_dir + curr_time + '/'
    # make output directory if doesnt exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    
    print('team_id: {0}, submission_id: {1}'.format(team_id, submission_id))
    
    config_dict = { 'team_id': team_id, 'submission_id': submission_id} 
    config_dict['timestamp'] = curr_time
    with open(output_dir + 'config.json', 'w') as file:
        file.write(json.dumps(config_dict))
    
    # get teamEpisodes dataframe
    rj, team_episodes_df = getTeamEpisodes(team_id)
    # filter on min_episodes
    team_episodes_df = team_episodes_df[team_episodes_df['id'] >= min_eps_id]
    
    print('Number of total team episodes: {0}'.format(len(team_episodes_df)))
    top_submit_df = team_episodes_df[team_episodes_df['submissionId'] == submission_id].reset_index(drop=True)
    print('Number of total submission episodes: {0}'.format(len(top_submit_df)))
    # iterate through list of episode ids and get json and save each
    for i in range(len(top_submit_df)):
        episode = top_submit_df['id'].iloc[i]
        saveEpisode_v2(episode, output_dir)
        
        
    end_time = round((time.time() - start_time), 2)
    print("complete: --- %s seconds ---" % end_time)
    

def run(team_id, submission_id, min_eps_id, output_dir):
    scrape_save_team_top_submit(team_id, submission_id, min_eps_id, output_dir)


    
# Script start here
team_id = 5653767 # WeKick
submission_id = 17747116
output_dir = 'episodes_dl/WeKick/sub_id_17747116/'
min_episode = 0
run(team_id, submission_id, min_episode, output_dir)