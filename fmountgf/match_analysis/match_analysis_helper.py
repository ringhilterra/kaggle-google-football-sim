import pandas as pd
import json
import numpy as np

from kaggle_environments.envs.football.helpers import Action

pd.set_option("display.float_format", lambda x: "%.5f" % x)
pd.options.display.max_rows = 999
pd.set_option('display.max_columns', 150)

np.set_printoptions(suppress=True)



# dictionary of sticky actions
sticky_actions = {
    "left": Action.Left,
    "top_left": Action.TopLeft,
    "top": Action.Top,
    "top_right": Action.TopRight,
    "right": Action.Right,
    "bottom_right": Action.BottomRight,
    "bottom": Action.Bottom,
    "bottom_left": Action.BottomLeft,
    "sprint": Action.Sprint,
    "dribble": Action.Dribble
}

action_set_dic = {
    0: 'idle',
    # movement actions (1-8)
    1: 'left', # run to the left, sticky action.
    2: 'top_left', #run to the top-left, sticky action.
    3: 'top', # run to the top, sticky action.
    4: 'top_right', # run to the top-right, sticky action.
    5: 'right', # run to the right, sticky action.
    6: 'bottom_right', # run to the bottom-right, sticky action.
    7: 'bottom', # run to the bottom, sticky action.
    8: 'bottom_left', # run to the bottom-left, sticky action
    
    # passing / shooting (9-12)
    9: 'long_pass', # perform a long pass to the player on your team. Player to pass the ball to is auto-determined based on the movement direction.
    10: 'high_pass', # perform a high pass, similar to long_pass.
    11: 'short_pass', # perform a short pass, similar to long_pass.
    12: 'shot', # perform a shot, always in the direction of the opponent's goal.
    
    13: 'sprint', # start sprinting, sticky action. Player moves faster, but has worse ball handling.
    14: 'release_direction', # reset current movement direction.
    15: 'release_sprint', # stop sprinting
    16: 'sliding', # perform a slide (effective when not having a ball)
    17: 'dribble', # start dribbling (effective when having a ball), sticky action. Player moves slower, but it is harder to take over the ball from him.
    18: 'release_dribble' # stop dribbling
}


# game_mode - current game mode, one of:
game_mode_dic = {
    0 : 'normal',
    1 : 'kickoff',
    2 : 'goalkick',
    3 : 'freekick',
    4 : 'corner',
    5 : 'throwin',
    6 : 'penalty'
}

# player roles
player_role_dic = {
    0: 'GK',
    1: 'CB',
    2: 'LB',
    3: 'RB',
    4: 'DM',
    5: 'CM',
    6: 'LM',
    7: 'RM',
    8: 'AM',
    9: 'CF'
}


def do_flatten(obj):
    if type(obj) == list:
        return np.array(obj).flatten()
    return obj.flatten()

def convert_observation(observation, fixed_positions=False):

    final_obs = []
    
    for obs in observation:

        o = []
        if fixed_positions:
            for i, name in enumerate(['left_team', 'left_team_direction',
                                    'right_team', 'right_team_direction']):
                o.extend(do_flatten(obs[name]))
            # If there were less than 11vs11 players we backfill missing values
            # with -1.
            if len(o) < (i + 1) * 22:
                o.extend([-1] * ((i + 1) * 22 - len(o)))
        else:
            o.extend(do_flatten(obs['left_team']))
            o.extend(do_flatten(obs['left_team_direction']))
            o.extend(do_flatten(obs['right_team']))
            o.extend(do_flatten(obs['right_team_direction']))

        # If there were less than 11vs11 players we backfill missing values with
        # -1.
        # 88 = 11 (players) * 2 (teams) * 2 (positions & directions) * 2 (x & y)
        if len(o) < 88:
            o.extend([-1] * (88 - len(o)))

        # ball position
        o.extend(obs['ball'])
        # ball direction
        o.extend(obs['ball_direction'])
        # one hot encoding of which team owns the ball
        if obs['ball_owned_team'] == -1:
            o.extend([1, 0, 0])
        if obs['ball_owned_team'] == 0:
            o.extend([0, 1, 0])
        if obs['ball_owned_team'] == 1:
            o.extend([0, 0, 1])

        active = [0] * 11
        if obs['active'] != -1:
            active[obs['active']] = 1
        o.extend(active)

        game_mode = [0] * 7
        game_mode[obs['game_mode']] = 1
        o.extend(game_mode)
        final_obs.append(o)

        return np.array(final_obs, dtype=np.float32).flatten()

    
def get_episode_simple115_v2_df(team_want, episode_id, episode_dir):
    # get json file for specific episode
    epsiode_full_dir = '{0}{1}.json'.format(episode_dir, episode_id)
    epsiode_full_dir

    with open(epsiode_full_dir) as json_file:
        obs = json.load(json_file)
        
    lteam = obs['info']['TeamNames'][0]
    rteam = obs['info']['TeamNames'][1]
    # want to get left or right based on agent
    if team_want ==  lteam:
        lr_index = 0
    else:
        lr_index = 1

    # want to get left or right based on agent
    if team_want ==  lteam:
        lr_index = 0
    else:
        lr_index = 1

    
    df = get_simple115_v2_df(obs)
    
    return df    


def get_simple115_v2_df(obs):
    steps = obs['steps']
    obs_list = []
    for step_num in range(len(steps)):
        observation = [steps[step_num][0]['observation']['players_raw'][0]]
        v2_115_obs = convert_observation(observation)
        obs_list.append(v2_115_obs)
       
    df_cols = get_simple115_v2_df_cols()
    df = pd.DataFrame(obs_list, columns=df_cols)
    return df



def get_simple115_v2_df_cols():
        # coords of left_team players (22)
    lcoords_col = []
    for i in range(11):
        lcoords_col.append('l_x' + str(i))
        lcoords_col.append('l_y' + str(i))
    # direction of left_team players (22)
    ldirs_col = []
    for i in range(11):
        ldirs_col.append('l_x_dir' + str(i))
        ldirs_col.append('l_y_dir' + str(i))
    # coords of right_team players (22)
    rcoords_col = []
    for i in range(11):
        rcoords_col.append('r_x' + str(i))
        rcoords_col.append('r_y' + str(i))
    # direction of left_team players (22)
    rdirs_col = []
    for i in range(11):
        rdirs_col.append('r_x_dir' + str(i))
        rdirs_col.append('r_y_dir' + str(i))
    # ball position (x,y,z)
    ball_pos = ['ball_x_pos', 'ball_y_pos', 'ball_z_pos']
    # ball direction (x,y,z)
    ball_dir = ['ball_x_dir', 'ball_y_dir', 'ball_z_dir']
    # one hot encoding of ball ownership (noone, left, right) (3)
    ball_own = ['ball_own_noone', 'ball_own_left', 'ball_own_right']
    # one hot encoding of which player is active (11)
    player_actives = ['p_active' + str(x) for x in range(11)]
    # one hot encoding of game mode (7)
    game_modes = ['gmode' + str(x) for x in range(7)]

    final_col_list = lcoords_col + ldirs_col + rcoords_col + rdirs_col + ball_pos + \
        ball_dir + ball_own + player_actives + game_modes
    
    return final_col_list


def get_episode_all_df(team_want, episode_id, episode_dir):
    
    # get json file for specific episode
    epsiode_full_dir = '{0}{1}.json'.format(episode_dir, episode_id)
    epsiode_full_dir

    with open(epsiode_full_dir) as json_file:
        obs = json.load(json_file)
      
    lteam = obs['info']['TeamNames'][0]
    rteam = obs['info']['TeamNames'][1]
    # want to get left or right based on agent
    if team_want ==  lteam:
        lr_index = 0
        agent_type = 'left'
    else:
        lr_index = 1
        agent_type = 'right'
    
    #create basic df
    steps = obs['steps']
    steps_lists = []

    for step_num in range(len(steps)):
        #print(i)
        step = steps[step_num]
        # get left or right player based on if matches team we want
        obs_step = step[lr_index]

        if step_num == 0:
            action = None
            action_str = None
        else:
            action = obs_step['action'][0]
            action_str = action_set_dic[action]
        

        status = obs_step['status']
        observation = obs_step['observation']
        players_raw = observation['players_raw'][0]
        
        active_player = players_raw['active']
        
        game_mode = players_raw['game_mode']
        game_mode_str = game_mode_dic[game_mode]

        # score
        left_score = players_raw['score'][0]
        right_score = players_raw['score'][1]

        # steps
        steps_left = players_raw['steps_left']
        
        # ball owned team  {-1, 0, 1}, -1 = ball not owned, 0 = left team, 1 = right team.
        ball_owned_team = players_raw['ball_owned_team']
        # we need to map ball owned based on if left or right agent
        if ball_owned_team == -1:
            off_def_flag = 'none'
        elif ball_owned_team == 0:
            off_def_flag = 'offense' if agent_type == 'left' else 'defense'
        elif ball_owned_team == 1:
            off_def_flag = 'offense' if agent_type == 'right' else 'defense'    

        # now create dataframe
        step_list = [step_num, action, action_str, game_mode_str, active_player, off_def_flag, left_score, right_score, agent_type, status]
        steps_lists.append(step_list)

        
    df_columns = ['step_num', 'action', 'action_str', 'game_mode_str', 'active_player', 'off_def_flag', 'left_score', 'right_score', 'agent_type', 'status']
    basic_df = pd.DataFrame(steps_lists, columns = df_columns)
    
    # get sidmple115_v2 embed df
    s115_df = get_simple115_v2_df(obs)
    s115_df['step_num'] = range(0, 3002)
    
    #merge
    final_df = pd.merge(basic_df, s115_df, how='outer', on=['step_num'])
    return final_df 