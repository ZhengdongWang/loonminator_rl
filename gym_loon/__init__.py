from gym.envs.registration import register

register(
    id='loon-v0',
    entry_point='gym_loon.envs:LoonEnv',
)
