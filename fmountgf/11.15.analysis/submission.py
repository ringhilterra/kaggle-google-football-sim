from math import sqrt, atan2, pi
from kaggle_environments.envs.football.helpers import *

directions = [
    Action.TopLeft,
    Action.Top,
    Action.TopRight,
    Action.Left,
    Action.Idle,
    Action.Right,
    Action.BottomLeft,
    Action.Bottom,
    Action.BottomRight,
]

goal_pos = [1, 0]

step = 0
obs_test = None
## helpers


def angle(src, tgt):
    xdir = tgt[0] - src[0]
    ydir = tgt[1] - src[1]
    theta = round(atan2(xdir, -ydir) * 180 / pi, 2)
    while theta < 0:
        theta += 360
    return theta


def direction(src, tgt):
    
    print('direction func, src: {0}, target: {1}'.format(src, tgt))
    theta = angle(src, tgt)
    print('theta: {0}:'.format(theta))

    if theta >= 360 - 22.5 or theta <= 0 + 22.5:
        return Action.Top
    if 45 - 22.5 <= theta <= 45 + 22.5:
        return Action.TopRight
    if 90 - 22.5 <= theta <= 90 + 22.5:
        return Action.Right
    if 135 - 22.5 <= theta <= 135 + 22.5:
        return Action.BottomRight
    if 180 - 22.5 <= theta <= 180 + 22.5:
        return Action.Bottom
    if 225 - 22.5 <= theta <= 225 + 22.5:
        return Action.BottomLeft
    if 270 - 22.5 <= theta <= 270 + 22.5:
        return Action.Left
    return Action.TopLeft


def get_distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5


def is_direction_set(sticky_actions):
    print("check if direction is set")
    if not sticky_actions:
        return False

    for action in sticky_actions:
        if action in directions:
            return True
    return False


# strategies


def in_shoot_pos(obs):
    # if in good shooting position return true
    active_player_pos = obs["left_team"][obs["active"]]
    active_player_x, active_player_y = active_player_pos

    if (active_player_x > 0.7) and (abs(active_player_y) < 0.2):
        return True
    else:
        return False


def shot_strategy(obs):
    # if in good shooting position
    if is_prepared_shot(obs):
        print("SHOOT")
        return Action.Shot
    else:
        return prepare_shot(obs)


def is_prepared_shot(obs):
    print("check if prepared for shot")
    player_pos = obs["left_team"][obs["active"]]
    face_dir = direction(player_pos, goal_pos)
    print('face_dir: {0}'.format(face_dir))
    # if sprinting and not facing goal and no players in the way
    if Action.Sprint in obs["sticky_actions"]:
        print(list(obs["sticky_actions"]))
        return False

    # after release sprint, release direction
    if is_direction_set(obs["sticky_actions"]):
        print("not prepared", "direction is set, want to release first")
        return False

    # if not facing goal direction return false
    # TO DO - determining angle player facing vs goal

    # if player in your way return false

    else:
        return True


def prepare_shot(obs):
    # if sprinting and not facing goal and no players in the way
    print("prepare shot")
    # first release sprint if sprinting
    if Action.Sprint in obs["sticky_actions"]:
        return Action.ReleaseSprint

    # then release direction if direction exists
    if is_direction_set(obs["sticky_actions"]):
        print("not prepared", "direction is set, want to release first")
        return Action.ReleaseDirection

    # then ensure direction facing goa

    # if all conditions before pass then return shot
    return Aciton.Shot


def offense_strategy(obs):
    # print('offense strategy')

    # if in good shooting position
    if in_shoot_pos(obs):
        print("in shoot position")
        return shot_strategy(obs)

    # if space to run into towards goal run

    # if open player upfield play longpass

    # if along the end lines and not a good angle to goal cross it

    return Action.Right  # default


def defense_strategy():
    print("defense strategy")
    # TO DO - run towards where ball and playe are going
    # OR run to between goal and player
    return Action.Idle


def offense_goal_kick_strategy():
    print("goal kick strategy")
    return Action.ShortPass


def offense_penalty_strategy():
    print("penalty strategy")
    return Action.Shot


def offense_corner_strategy():
    print("corner strategy")
    return Action.LongPass


def offense_kickoff_strategy():
    print("kickoff strategy")
    return Action.ShortPass


def offense_throw_in_strategy():
    print("throw in strategy")
    return Action.ShortPass


# get agent_strategy()
def get_agent_strategy():
    # TO DO
    return True


## agent def


@human_readable_agent
def agent(obs):
    global step
    step += 1
    print(step)
    # print(obs['sticky_actions'])
    ball_pos = obs["ball"]
    active_player_pos = obs["left_team"][obs["active"]]
    active_player_x, active_player_y = active_player_pos

    ball_owned = obs[
        "ball_owned_team"
    ]  #  -1 = ball not owned, 0 = left team, 1 = right team.
    # print('ball_owned:{0}'.format(ball_owned))

    if step == 1:
        return Action.Top
    if 6 >= step >= 2:
        return Action.Sprint
    if  8 >= step >= 6:
        return Action.TopRight

    # if step == 24:
    #     return Action.ReleaseSprint

    # #if step == 25:
    # #    return Action.ReleaseDirection

    # if 25 <= step <= 29:
    #     return Action.Bottom

    # if step == 30:
    #     return Action.Shot

    if ball_owned == 0:
        return offense_strategy(obs)

    else:
        return Action.Right
