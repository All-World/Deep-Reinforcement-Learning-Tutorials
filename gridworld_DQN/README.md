# Training an Agent to beat GridWorld using Deep Q-Networks (`gridworld_DQN.py`)

We train an agent to beat Grid World using deep Q-networks (keras). This is scalable neural network upgrade to classical tabular methods as used in our previous Grid World examples:

* [Training an Agent to beat GridWorld (`gridworld.py`)](https://github.com/ankonzoid/Deep-Reinforcement-Learning-Tutorials/blob/master/gridworld)

* [Solving the Hunter-Prey problem as a single-agent problem using relative coordinates (`hunterprey.py`)](https://github.com/ankonzoid/Deep-Reinforcement-Learning-Tutorials/blob/master/hunterprey)

In deep policy network methods, the policy network outputs the estimated action probabilities via a feed-forwarding of a state. Its weights are the generalization of the matrix values in tabular methods, and are responsible for convert the input state into a softmax policy vector of action probabilities. The scalability of the policy network comes from the aspect of treating the problem as one of regression and finding patterns that are past the storage of Q(*s*,*a*) values. The downsides of deep policy networks however are the ones that typically come with training a neural network *i.e. you have to choose the right architectures, losses, optimizers, training samples, etc.*

We provide two alternative agent policy selection modes of *epsilon-greedy selection* (`"policy_mode": "epsilongreedy"`) and *softmax selection* (`"policy_mode": "softmax"`). For a given state *s*, the:

* Epsilon-greedy agent chooses a random action at epsilon probability, otherwise it acts greedily by choosing action argmax{a} Q(s,a).

* Boltzmann (softmax) agent samples for an action *a* from the probabilities proportional to the values of Q(s,a). 

### Example output:

For grid size of (20, 20) set by `env_info = {"Ny": 20, "Nx": 20}`, we train the agent to find move from the top-left corner to the bottom-right corner in 1000 training episodes with a exponentially-decaying epsilon exploration parameter. 

For epsilon-greedy selection:

```
[episode 0] mode = epsilongreedy, iter = 6710, epsilon = 1.0000, reward = 32.91
[episode 1] mode = epsilongreedy, iter = 2812, epsilon = 0.9954, reward = 71.89
[episode 2] mode = epsilongreedy, iter = 2178, epsilon = 0.9908, reward = 78.23
[episode 3] mode = epsilongreedy, iter = 932, epsilon = 0.9863, reward = 90.69
...
...
...
[episode 997] mode = epsilongreedy, iter = 38, epsilon = 0.0101, reward = 99.63
[episode 998] mode = epsilongreedy, iter = 38, epsilon = 0.0101, reward = 99.63
[episode 999] mode = epsilongreedy, iter = 38, epsilon = 0.0100, reward = 99.63
```

For softmax selection (it converges to optimal early because it is adaptively greedy):

```
[episode 0] mode = softmax, iter = 9868, reward = 1.33
[episode 1] mode = softmax, iter = 4208, reward = 57.93
[episode 2] mode = softmax, iter = 2488, reward = 75.13
[episode 3] mode = softmax, iter = 572, reward = 94.29
...
...
...
[episode 129] mode = softmax, iter = 38, reward = 99.63
[episode 130] mode = softmax, iter = 38, reward = 99.63
[episode 131] mode = softmax, iter = 38, reward = 99.63
...
...
...
```

Both policy modes end up giving the optimal number of actions (`iter`) in an episode of Ny + Nx - 1 = 38 for our (20, 20) grid square.

### Usage:

> python gridworld_DPG.py

### Libraries required:

* keras

* numpy
