from kaggle_environments.envs.football.helpers import *
from random import randint


# Function to calculate distance 
def get_distance(pos1,pos2):
    return (((pos1[0]-pos2[0])**2)+((pos1[1]-pos2[1])**2))**0.5

# Function to cross ball from wing
def cross_ball():
    pass

# Movement directions
directions = [
[Action.TopLeft, Action.Top, Action.TopRight],
[Action.Left, Action.Idle, Action.Right],
[Action.BottomLeft, Action.Bottom, Action.BottomRight]]

dirsign = lambda x: 1 if abs(x) < 0.01 else (0 if x < 0 else 2)

# Set game plan parameters
goalRange = 0.65
wingRange = 0.21

@human_readable_agent
def agent(obs):
    
    # Add direction to action
    def sticky_check(action, direction):
        if direction in obs['sticky_actions']:
            return action
        else:
            return direction
    
    controlled_player_pos = obs['left_team'][obs['active']]
    
    
    # Pass when KickOff or ThrowIn
    if obs['game_mode'] == GameMode.KickOff or obs['game_mode'] == GameMode.ThrowIn:
        return sticky_check(Action.ShortPass, Action.Right) 
    
    # Shoot when freekick in goal range; If on wing then cross; Otherwise just pass
    if obs['game_mode'] == GameMode.FreeKick:
        # Shoot if in range
        if controlled_player_pos[0] > goalRange and controlled_player_pos[1] < wingRange and controlled_player_pos[1] > -(wingRange):
            ydir = randint(0,2)
            return sticky_check(Action.Shot, directions[ydir][2]) 
        # Cross from right
        if controlled_player_pos[0] > goalRange and controlled_player_pos[1] > wingRange:
            return sticky_check(Action.HighPass, Action.TopRight)
        
        # Cross from left
        if controlled_player_pos[0] > goalRange and controlled_player_pos[1] < -(wingRange):
            return sticky_check(Action.HighPass, Action.BottomRight)
    
    # Cross in for corner
    if obs['game_mode'] == GameMode.Corner and obs['ball'][1] < 0:
        return sticky_check(Action.HighPass, Action.Bottom)
    elif obs['game_mode'] == GameMode.Corner and obs['ball'][1] > 0:
        return sticky_check(Action.HighPass, Action.Top)
        
    # High pass when GoalKick 
    if obs['game_mode'] == GameMode.GoalKick:
        ydir = randint(0,2)
        return sticky_check(Action.HighPass, directions[ydir][2])
    
    # Shoot when Penalty
    if obs['game_mode'] == GameMode.Penalty:
        xdir = randint(0,2)
        ydir = randint(0,2)
        return sticky_check(Action.Shot, directions[ydir][xdir])
    
    # Make sure player is running.
    if Action.Sprint not in obs['sticky_actions']:
        return Action.Sprint
    # We always control left team (observations and actions
    # are mirrored appropriately by the environment).
    controlled_player_pos = obs['left_team'][obs['active']]
    
    # Check if we are in possession
    if obs['ball_owned_player'] == obs['active'] and obs['ball_owned_team'] == 0:
        
        # Clear if we are near our goal
        if controlled_player_pos[0] < -(goalRange):
            return sticky_check(Action.HighPass, Action.Right)
        
        # Shoot if we are in the final third and not at an acute angle
        if controlled_player_pos[0] > goalRange and controlled_player_pos[1] < wingRange and controlled_player_pos[1] > -(wingRange):
            ydir = randint(0,2)
            return sticky_check(Action.Shot, directions[ydir][2])
        #if the goalie is coming out on player near goal shoot
        elif obs['right_team'][0][0] < 0.8 or abs(obs['right_team'][0][1]) > 0.05:
            return Action.Shot
        
        # Cross from right
        if controlled_player_pos[0] > goalRange and controlled_player_pos[1] > wingRange:
            return sticky_check(Action.HighPass, Action.TopRight)
        
        # Cross from left
        if controlled_player_pos[0] > goalRange and controlled_player_pos[1] < -(wingRange):
            return sticky_check(Action.HighPass, Action.BottomRight)
        
        # Run towards the goal otherwise.
        return Action.Right
    else:
        #where ball is going we add the direction xy to ball current location
        ball_targetx=obs['ball'][0]+(1.5 * obs['ball_direction'][0])
        ball_targety=obs['ball'][1]+(1.5 * obs['ball_direction'][1])

        # Euclidian distance to ball
        e_dist=get_distance(obs['left_team'][obs['active']],obs['ball'])

        if e_dist >.005:
            # Run where ball will be
            xdir = dirsign(ball_targetx - controlled_player_pos[0])
            ydir = dirsign(ball_targety - controlled_player_pos[1])
            return directions[ydir][xdir]
        else:
            prob = randint(0,100)
            if prob > 70 and controlled_player_pos[0] < obs['right_team'][obs['active']][0]:
                return Action.Slide
            # Run towards the ball.
            xdir = dirsign(obs['ball'][0] - controlled_player_pos[0])
            ydir = dirsign(obs['ball'][1] - controlled_player_pos[1])
            return directions[ydir][xdir]
