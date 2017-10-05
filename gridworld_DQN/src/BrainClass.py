"""

 BrainClass.py  (author: Anson Wong / git: ankonzoid)

"""
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Reshape, Flatten
from keras.layers.convolutional import Convolution2D

class Brain():

    def __init__(self, env, brain_info):

        # Training Parameters
        self.gamma = brain_info["discount"]
        self.learning_rate = brain_info["learning_rate"]

        # Q function
        self.Q = self._build_Q(env)

    def _build_Q(self, env):

        # Build DQN architecture (outputs [Q(a_1), Q(a_2), ..., Q(a_n)])
        Q = Sequential()
        Q.add(Reshape((1, env.Ny, env.Nx), input_shape=(env.Ny, env.Nx)))  # Reshape 2D to 3D slice
        Q.add(Convolution2D(64, (2, 2), strides=(1, 1), padding="same", activation="relu", kernel_initializer="he_uniform"))
        Q.add(Flatten())
        Q.add(Dense(64, activation="relu", kernel_initializer="he_uniform"))
        Q.add(Dense(32, activation="relu", kernel_initializer="he_uniform"))
        Q.add(Dense(env.action_size, activation="softmax"))

        # Select optimizer and loss function
        Q.compile(loss="binary_crossentropy", optimizer="Adam")

        # Print QNN architecture summary
        Q.summary()

        return Q


    def update_Q(self, memory):
        states = memory.state_memory
        actions = memory.action_memory
        rewards = memory.reward_memory
        Qprobs = memory.Qprob_memory
        probs = memory.prob_memory

        gamma = self.gamma
        learning_rate = self.learning_rate

        def compute_gradients(actions, probs):
            # The gradient is the correction in the action probabilities
            # gradient = onehotvec(a) - prob
            def gradient(action, prob):
                y = np.zeros([prob.shape[0]])
                y[action] = 1
                gradient = np.array(y).astype('float32') - prob
                return gradient

            gradients = []
            for (action, prob) in zip(actions, probs):
                gradients.append(gradient(action, prob))
            return gradients

        def compute_discounted_rewards_total(rewards, gamma):
            # If rewards = [r(0), r(1), r(2), ..., r(n-2), r(n-1), r(n)]
            # Then discounted rewards = [..., r(n-2) + gamma*r(n-1) + gamma^2*r(n), r(n-1) + gamma*r(n), r(n)]
            # We compute this by going through the list in reverse order
            rewards_total = [0.0] * len(rewards)
            rsum = 0.0
            for t in reversed(range(len(rewards))):
                rsum = rewards[t] + gamma * rsum
                rewards_total[t] = rsum
            return rewards_total

        # Compute intermediate quantities, and vertically stack as row vector matrix (2D)
        gradients = np.vstack(compute_gradients(actions, probs))
        discounted_rewards_total = np.vstack(compute_discounted_rewards_total(rewards, gamma))
        discounted_rewards_total /= np.std(discounted_rewards_total)

        # Compute loss scaled by discounted rewards
        loss = discounted_rewards_total * gradients

        # Construct training data of states
        X = np.squeeze(np.vstack([states]))

        # Construct labels by adding loss
        dQprobs = learning_rate * np.squeeze(np.vstack([loss]))
        Y = Qprobs + dQprobs

        # Train Q network
        self.Q.train_on_batch(X, Y)

    # ==================================
    # IO functions
    # ==================================

    def load_Q(self, filename):
        self.Q.load_weights(filename)

    def save_Q(self, filename):
        self.Q.save_weights(filename)