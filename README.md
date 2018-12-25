# Loon Reinforcement Learning Environment

The Game Loonminator played by AI.

Made for [OpenAI Gym](https://gym.openai.com).

Play the game as a human [here](https://github.com/ZhengdongWang/loonminator).

# Installation

Requires [TensorFlow](https://www.tensorflow.org/install/), [Keras](https://keras.io/#installation), [keras-rl](https://github.com/keras-rl/keras-rl), and numpy.

After following those instructions, run setup with:
```
pip install -e '.[all]
```

Copy the repository file structure to ensure imports work correctly.

```
loonminator_rl
│	README.md # this file
|	loonminator_rl.ipynb # rl network
│	setup.py # install dependencies
|	winds.py # GFS winds for the environment
│	...
└───gym_loon
|	|	...
│	└───envs
│		│	loon_env.py # custom environment for gym
│		│	...
│
└───...
```
