from kaggle_environments.envs.football.helpers import *
from random import choice,seed

seed(0) # For testing purpose

memory = []
notRunning = [False,0]

@human_readable_agent
def agent(obs):
    # Execute memorized actions
    global memory
    if memory:
        return memory.pop(0)
    
    # Execute a sequence of actions
    def do_actions(sequence):
        global memory
        memory = sequence[1:]
        return sequence[0]

    # Execute an actions in proper direction
    def do_sticky(direction, action):
        if direction in obs['sticky_actions']:
            return action
        return do_actions([direction,action])

    # Evaluate euclidian distance between two objects
    def get_distance(pos1,pos2):
        return ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**0.5
    
    # Get distance to closer opponent
    def get_closer_opponent_dist():
        closer_opponent_dist = 3
        for opponent_pos in obs['right_team']:
            closer_opponent_dist = min(get_distance(controlled_player_pos,opponent_pos),closer_opponent_dist)
        return closer_opponent_dist
    
    # Estimate landing position
    def ball_landing_pos():
        start_height = obs['ball'][2]
        end_height = 0.5
        start_speed = obs['ball_direction'][2]
        gravity = 0.1
        time = (start_speed**2/gravity**2 - 2/gravity*(end_height-start_height))**0.5 + start_speed/gravity
        return [obs['ball'][0]+obs['ball_direction'][0]*time, obs['ball'][1]+obs['ball_direction'][1]*time]
    
    # Estimate interception point
    def ball_intercept_pos():
        if get_distance(controlled_player_pos,obs['ball']) > 0.1:
            steps = 5
            return [obs['ball'][0]+steps*obs['ball_direction'][0],obs['ball'][1]+steps*obs['ball_direction'][1]]
        return [obs['ball'][0],obs['ball'][1]] 
    
    # Estimate ball movement to intercept
    def estimate_ball_pos():
        if obs['ball'][2] > 0.5:
            return ball_landing_pos()
        return ball_intercept_pos()
    
    controlled_player_pos = obs['left_team'][obs['active']]
    
    # Fix gameMode switch to normal before the game restart
    global notRunning
    if obs['game_mode'] != GameMode.Normal:
        notRunning = [True,obs['game_mode']]
    elif notRunning[0] and (obs['ball_direction'][0] != 0 or obs['ball_direction'][1] != 0):
        notRunning = [False,0]
    
    # Game Stopped
    if notRunning[0]:
        # KickOff strategy: short pass back or side
        if notRunning[1] == GameMode.KickOff:
            return do_actions([choice([Action.Left, Action.Top if controlled_player_pos[1] > 0 else Action.Bottom]),Action.ShortPass])
        # Penalty strategy: make a shot
        if notRunning[1] == GameMode.Penalty:
            return do_actions([choice([Action.TopRight,Action.BottomRight,Action.Right]),Action.Shot])
        # Goalkick strategy: long pass to front
        if notRunning[1] == GameMode.GoalKick:
            return do_actions([choice([Action.TopRight,Action.BottomRight,Action.Right]),choice([Action.LongPass,Action.HighPass])])
        # Freekick strategy: long pass when back to the middle, and short pass when in front
        if notRunning[1] == GameMode.FreeKick:
            action = [Action.ShortPass] if controlled_player_pos[0] > 0 else [choice([Action.LongPass,Action.HighPass])]
            if abs(controlled_player_pos[1]) < 0.2:
                action.insert(0,choice([Action.Right,Action.TopRight,Action.BottomRight]))
            else:
                action.insert(0,choice([Action.Right,Action.TopRight]) if controlled_player_pos[1] > 0 else choice([Action.Right,Action.BottomRight]))
            return do_actions(action)
        # Corner strategy: high pass to goal area
        if notRunning[1] == GameMode.Corner:
            return do_actions([Action.Top if controlled_player_pos[1] > 0 else Action.Bottom , Action.HighPass])
        # Throwin strategy: short pass into field
        if notRunning[1] == GameMode.ThrowIn:
            return do_actions([choice([Action.Top,Action.TopRight]) if controlled_player_pos[1] > 0 else choice([Action.Bottom,Action.BottomRight]) , Action.ShortPass])
    
    # Playing
    # Always run
    if Action.Sprint not in obs['sticky_actions'] and controlled_player_pos[0] < 0.5:
        return Action.Sprint
    
    # We have the ball
    if obs['ball_owned_player'] == obs['active'] and obs['ball_owned_team'] == 0:
        if controlled_player_pos[0] > 0.3:
            if abs(controlled_player_pos[1]) > 0.2:
                return Action.TopRight if controlled_player_pos[1] > 0 else Action.BottomRight
            if controlled_player_pos[0] > 0.4:
                opponent_gk_pos = obs['right_team'][0]
                if opponent_gk_pos[0] < 0.8:
                    return do_actions([Action.ReleaseSprint,choice([Action.TopLeft,Action.BottomLeft]),Action.Right,Action.Shot])
            if Action.Sprint in obs['sticky_actions'] and controlled_player_pos[0] > 0.5:
                    return Action.ReleaseSprint
            if get_distance(controlled_player_pos,[1,0]) < 0.4:
                return do_sticky(Action.Right,Action.Shot)
        return Action.Right
    
    # Opponents have the ball
    elif obs['ball_owned_team'] == 1:
        # Move to the ball but no right
        if obs['ball'][0] > controlled_player_pos[0] + 0.1:
            if obs['ball'][1] > controlled_player_pos[1]:
                return Action.Bottom
            if obs['ball'][1] < controlled_player_pos[1]:
                return Action.Top
        elif obs['ball'][0] > controlled_player_pos[0]:
            if obs['ball'][1] > controlled_player_pos[1]:
                return Action.BottomLeft
            if obs['ball'][1] < controlled_player_pos[1]:
                return Action.TopLeft
        elif obs['ball'][0] < controlled_player_pos[0]:
            if obs['ball'][1] > controlled_player_pos[1]:
                return Action.BottomLeft
            if obs['ball'][1] < controlled_player_pos[1]:
                return Action.TopLeft
        return Action.Left
    
    # None have the ball
    else:
        # Move to the ball
        estimated_ball_pos = estimate_ball_pos()
        if estimated_ball_pos[0] > controlled_player_pos[0]:
            if estimated_ball_pos[1] > controlled_player_pos[1]:
                return Action.BottomRight
            if estimated_ball_pos[1] < controlled_player_pos[1]:
                return Action.TopRight
            return Action.Right
        if estimated_ball_pos[0] < controlled_player_pos[0]:
            if estimated_ball_pos[1] > controlled_player_pos[1]:
                return Action.BottomLeft
            if estimated_ball_pos[1] < controlled_player_pos[1]:
                return Action.TopLeft
            return Action.Left
    
    return Action.Idle