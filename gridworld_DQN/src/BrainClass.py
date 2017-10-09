"""

 BrainClass.py  (author: Anson Wong / git: ankonzoid)

"""
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Reshape, Flatten
from keras.layers.convolutional import Convolution2D
from keras.models import load_model

class Brain:

    def __init__(self, env, info):

        # Training Parameters
        self.brain_info = info["brain"]
        self.env_info = info["env"]

        # Learning parameters
        self.gamma = self.brain_info["discount"]
        self.learning_rate = self.brain_info["learning_rate"]

        # Model network function
        self.MN = self._build_MN(env)

    def _build_MN(self, env):
        input_dim_2D = env.state_dim
        input_dim_3D = (1,) + env.state_dim
        output_size = env.action_size
        # Build model architecture (outputs [M(a_1), M(a_2), ..., M(a_n)])
        MN = Sequential()
        MN.add(Reshape(input_dim_3D, input_shape=input_dim_2D))  # Reshape 2D to 3D slice
        MN.add(Convolution2D(64, (2, 2), strides=(1, 1), padding="same", activation="relu", kernel_initializer="he_uniform"))
        MN.add(Flatten())
        MN.add(Dense(64, activation="relu", kernel_initializer="he_uniform"))
        MN.add(Dense(32, activation="relu", kernel_initializer="he_uniform"))
        MN.add(Dense(output_size, activation="linear"))
        # Select optimizer and loss function
        MN.compile(loss="binary_crossentropy", optimizer="Adam")
        # Print model network architecture summary
        MN.summary()
        return MN

    def update(self, memory, env):


        states = memory.state_memory
        states_next = memory.state_next_memory
        actions = memory.action_memory
        rewards = memory.reward_memory
        MN_outputs = memory.MN_output_memory

        gamma = self.gamma
        learning_rate = self.learning_rate

        # Compute loss scaled by discounted rewards
        losses = []
        for i, (state, state_next, action, reward) in enumerate(zip(states, states_next, actions, rewards)):

            # Compute Q_max_next
            if env.is_terminal_state(state_next):
                Q_max_next = 0.0
            else:
                state_next_reshaped = state_next.reshape(list((1,) + env.state_dim))
                Q_state_next = self.MN.predict(state_next_reshaped, batch_size=1).flatten()
                Q_max_next = np.max(Q_state_next)

            # Current Q estimates
            Q = MN_outputs

            # Target Q
            Q_target = np.zeros_like(MN_outputs)
            Q_target[action] = reward + gamma*Q_max_next

            # Loss function
            loss = np.square(Q_target - Q)
            losses.append(loss)

        # Construct training data (states)
        X = np.squeeze(np.vstack([states]))

        # Construct training labels (loss)
        dMN_outputs = learning_rate * np.squeeze(np.vstack([losses]))
        #MN_outputs = np.array(MN_outputs, dtype=np.float32)

        Y = MN_outputs + dMN_outputs

        # Train Q network
        self.MN.train_on_batch(X, Y)

    # ==================================
    # IO functions
    # ==================================

    def load_MN(self, filename):
        self.MN = load_model(filename)
        self.MN.compile(loss="binary_crossentropy", optimizer="Adam")
        self.MN.summary()

    def save_MN(self, filename):
        self.MN.save(filename)