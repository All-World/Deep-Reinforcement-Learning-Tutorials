"""

 hunterprey.py  (author: Anson Wong / git: ankonzoid)

 Trains a hunter agent to capture a prey agent on an (Ny, Nx) grid.

"""
import numpy as np
import matplotlib
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from EpsilonGreedy_AgentClass import Agent
from HunterPrey_EnvironmentClass import Environment
from MemoryClass import Memory
import utils

def main():
    # =========================
    # Settings
    # =========================
    learning_mode = "SampleAveraging"

    if learning_mode == "SampleAveraging":

        from SampleAveraging_BrainClass import Brain
        N_episodes_train = 100000
        N_episodes_test = 30
        agent_info = {"name": "hunter", "epsilon": 0.5}
        env_info = {"N_global": 7}
        brain_info = {}

    elif learning_mode == "QLearning":

        from QLearning_BrainClass import Brain
        N_episodes_train = 10000
        N_episodes_test = 30
        agent_info = {"name": "hunter", "epsilon": 0.5}
        env_info = {"N_global": 7}
        brain_info = {"learning_rate": 0.8, "discount": 0.9}  # only relevant for Q-learning

    else:
        raise IOError("Error: Invalid learning mode!")

    save_video = True
    video_file = "results/hunterprey.mp4"
    convert_mp4_to_gif = True
    gif_file = "results/hunterprey.gif"

    # =========================
    # Set up environment, agent, memory and brain
    # =========================
    agent = Agent(agent_info)
    env = Environment(env_info)
    brain = Brain(env, brain_info)
    memory = Memory(env)

    # =========================
    # Train agent
    # =========================
    print("\nTraining '{}' agent on '{}' environment for {} episodes, testing for {} episodes (epsilon = {})...\n".format(agent.name, env.name, N_episodes_train, N_episodes_test, agent.epsilon))

    memory.reset_run_counters()  # reset run counters once only
    state_global_history_video = []
    state_target_global_history_video = []
    for episode in range(N_episodes_train + N_episodes_test):
        if (episode >= N_episodes_train):
            agent.epsilon = 0  # set no exploration for test episodes
        memory.reset_episode_counters()  # reset episodic counters

        # state = position of hunter relative to prey (want to get to [0,0])
        # state_global = global position of hunter
        # state_target_global = global position of prey
        if episode == 0:
            (state, state_global, state_target_global) = env.get_random_state()
        else:
            (state, state_global, state_target_global) = env.get_random_state(set_state_global=state_global)
        env.set_state_terminal_global(state_target_global)

        state_global_history = [state_global]
        n_iter_episode = 0
        while not env.is_terminal(state):  # NOTE: terminates when hunter hits local coordinates of (0,0)
            # Get action from policy
            action = agent.get_action(state, brain, env)  # get action from policy
            # Collect reward from environment
            reward = env.get_reward(state, action)  # get reward
            # Update episode counters
            memory.update_episode_counters(state, action, reward)  # update our episodic counters
            # Compute and observe next state
            state_next = env.perform_action(state, action)
            state_global_next = env.perform_action_global(state_global, action)
            # Update Q after episode (if needed)
            if "update_Q_during_episode" in utils.method_list(Brain):
                brain.update_Q_during_episode(state, action, state_next, reward)
            # Transition to next state
            state = state_next
            state_global = state_global_next
            # Track states for video
            state_global_history.append(state_global)
            # Exit program if testing fails (bad policy)
            n_iter_episode += 1
            if (episode >= N_episodes_train) and (n_iter_episode > 2000):
                raise IOError("Bad policy found! Non-terminal episode!")

        # Append for video output
        if episode >= N_episodes_train:
            state_global_history_video.append(state_global_history)
            state_target_global_history_video.append([state_target_global] * len(state_global_history))

        # Update run counters first (before updating Q)
        memory.update_run_counters()  # use episode counters to update run counters

        # Update Q after episode (if needed)
        if "update_Q_after_episode" in utils.method_list(Brain):
            brain.update_Q_after_episode(memory)

        # Give output to user on occasion
        if (episode + 1) % (N_episodes_train / 20) == 0 or (episode >= N_episodes_train):
            n_optimal = np.abs(env.ygrid_global[state_global_history[0][0]] - env.ygrid_global[state_target_global[0]]) + np.abs(env.xgrid_global[state_global_history[0][1]] - env.xgrid_global[state_target_global[1]])

            # =====================
            # Print text
            # =====================
            mode = "train" if(episode < N_episodes_train) else "test"
            print(" [{} episode = {}/{}] epsilon = {}, total reward = {:.1F}, n_actions = {}, n_optimal = {}, grid goal: [{},{}] -> [{},{}]".format(mode, episode + 1, N_episodes_train + N_episodes_test, agent.epsilon, memory.R_total_episode, memory.N_actions_episode, n_optimal, env.ygrid_global[state_global_history[0][0]], env.xgrid_global[state_global_history[0][1]], env.ygrid_global[state_target_global[0]], env.xgrid_global[state_target_global[1]]))

    # =====================
    # Make video animation
    # =====================
    if save_video:
        print("\nSaving file to '{}'...".format(video_file))
        plot_hunter_prey(state_global_history_video,
                         state_target_global_history_video,
                         env, video_file=video_file)

        if convert_mp4_to_gif:
            print("\nConverting '{}' to '{}'...".format(video_file, gif_file))
            import moviepy.editor as mp
            clip = mp.VideoFileClip(video_file)
            clip.write_gif(gif_file)


# ===================
# Plotting function
# ===================
def plot_hunter_prey(state_global_history_video,
                     state_target_global_history_video,
                     env, video_file="hunterprey.mp4"):
    import matplotlib.animation as animation
    import matplotlib.pyplot as plt
    import numpy as np

    # Flatten
    state_global_history_video_flat = \
        [item for sublist in state_global_history_video for item in sublist]
    state_target_global_history_video_flat = \
        [item for sublist in state_target_global_history_video for item in sublist]

    fig, ax = plt.subplots(1, 1, tight_layout=True)

    def updatefig(i):
        # Clear figure
        ax.clear()

        # Plot
        s_hunter = state_global_history_video_flat[i]
        s_prey = state_target_global_history_video_flat[i]
        hunter_coord = (env.ygrid_global[s_hunter[0]], env.xgrid_global[s_hunter[1]])
        prey_coord = (env.ygrid_global[s_prey[0]], env.xgrid_global[s_prey[1]])

        N = env.Ny_global
        data = np.ones((N, N)) * np.nan
        color_dict = {"blue": 0, "red": 1}
        data[hunter_coord] = color_dict["blue"]  # blue
        data[prey_coord] = color_dict["red"]  # red

        my_cmap = matplotlib.colors.ListedColormap(['b', 'r'])
        my_cmap.set_bad(color='w', alpha=0)
        for x in range(N + 1):
            ax.axhline(x, lw=2, color='k', zorder=5)
            ax.axvline(x, lw=2, color='k', zorder=5)
        ax.imshow(data, interpolation='none', cmap=my_cmap, extent=[0, N, 0, N], zorder=0)
        ax.axis('off')

        # Draw
        plt.draw()

    anim = animation.FuncAnimation(fig, updatefig, len(state_global_history_video_flat))
    anim.save(video_file, fps=10)

# Driver
if __name__ == '__main__':
    main()