'''
Project: examples
Created Date: Sunday, December 23rd 2018, 11:25:57 pm
Author: Zhefan Ye <zhefanye@gmail.com>
-----
Copyright (c) 2018 TBD
Do whatever you want
'''
import numpy as np
from ple import PLE
from ple.games.simpleshooter import SimpleShooter


class ShootAgent():
    """
            This is our naive agent. It picks actions at random!
    """

    def __init__(self, actions):
        self.actions = actions

    def pickAction(self, reward, obs):
        return self.actions[np.random.randint(0, len(self.actions))]


###################################
game = SimpleShooter(width=640, height=480)  # create our game

fps = 30  # fps we want to run at
frame_skip = 2
num_steps = 1
force_fps = False  # slower speed
display_screen = True

reward = 0.0
max_noops = 20
nb_frames = 15000


def process_state(state):
    return np.array([state["player_y"], state["player_velocity"], state["target_y"],
                     state["bullet_x"], state["bullet_y"], state["bullet_velocity_x"],
                     state["bullet_velocity_y"]])


# make a PLE instance.
p = PLE(game, fps=fps, frame_skip=frame_skip, num_steps=num_steps,
        force_fps=force_fps, display_screen=display_screen,
        state_preprocessor=process_state)

# shooting agent
agent = ShootAgent(p.getActionSet())

# init agent and game.
p.init()

# lets do a random number of NOOP's
for i in range(np.random.randint(0, max_noops)):
    reward = p.act(p.NOOP)

# start our training loop
for f in range(nb_frames):
    # if the game is over
    if p.game_over():
        p.reset_game()
        print('game over')

    obs = p.getScreenRGB()
    state = p.getGameState()
    print(state)
    action = agent.pickAction(reward, obs)
    reward = p.act(action)
#     print('score: {}'.format(reward))
