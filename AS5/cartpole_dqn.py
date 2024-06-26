import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import gym

from plot import draw


#====== code segment starts ======

N_EPISODES = 400
EPISODE_LENGTH = 200

#====== code segment ends ======

def save_hidden_nodes(nodes):
    data = {
        "num_hidden_nodes": nodes
    }

    with open('cartpole_dqn.json', 'w', encoding = 'utf-8') as f:
        json.dump(data, f, ensure_ascii = False, indent = 4)


# Basic Q-netowrk
class Net(nn.Module):
    def __init__(self, n_states, n_actions, n_hidden):
        super(Net, self).__init__()

        save_hidden_nodes(n_hidden)

        #====== code segment starts ======

        # Two fully-connected layers, input (state) to hidden & hidden to output (action)
        self.fc1 = nn.Linear(n_states, n_hidden)
        self.out = nn.Linear(n_hidden, n_actions)

        #====== code segment ends ======

        nn.init.xavier_normal_(self.fc1.weight)
        nn.init.xavier_normal_(self.out.weight)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        action_values = self.out(x)
        return action_values


# Deep Q-Network, composed of one eval network, one target network
class DQN(object):
    def __init__(self, n_states, n_actions, n_hidden, batch_size, lr, epsilon, gamma, target_replace_iter, memory_capacity):

        #====== code segment starts ======

        self.eval_net, self.target_net = Net(n_states, n_actions, n_hidden), Net(n_states, n_actions, n_hidden)

        self.memory = np.zeros((memory_capacity, n_states*2+2)) # initialize memory, each memory slot is of size (state + next state + reward + action)
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr = lr)
        self.loss_func = nn.MSELoss()
        self.memory_counter = 0
        self.learn_step_counter = 0 # for target network update

        self.n_states = n_states
        self.n_actions = n_actions
        self.n_hidden = n_hidden
        self.batch_size = batch_size
        self.lr = lr
        self.epsilon = epsilon
        self.gamma = gamma
        self.target_replace_iter = target_replace_iter
        self.memory_capacity = memory_capacity

        #====== code segment ends ======

    def choose_action(self, state):
        x = torch.unsqueeze(torch.tensor(state, dtype=torch.float), 0)

        #====== code segment starts ======

        # epsilon-greedy
        if np.random.uniform() < self.epsilon:  # random
            action = np.random.randint(0, self.n_actions)
        else: 
            action_values = self.eval_net(x)              # feed into eval net, get scores for each action
            action = torch.argmax(action_values).item()   # choose the one with the largest score

        #====== code segment ends ======

        return action

    def store_transition(self, state, action, reward, next_state):

        #====== code segment starts ======

        # Pack the experience
        transition = np.hstack((state, [action,reward], next_state))

        # Replace the old memory with new memory
        index = self.memory_counter % self.memory_capacity
        self.memory[index, :] = transition
        self.memory_counter += 1

        #====== code segment ends ======

    def learn(self):
        # Randomly select a batch of memory to learn from
        sample_index = np.random.choice(self.memory_capacity, self.batch_size)
        b_memory = self.memory[sample_index, :]
        b_state = torch.tensor(b_memory[:, : self.n_states], dtype=torch.float)
        b_action = torch.tensor(b_memory[:, self.n_states : self.n_states + 1], dtype = torch.long)
        b_reward = torch.tensor(b_memory[:, self.n_states + 1 : self.n_states + 2], dtype = torch.float)
        b_next_state = torch.tensor(b_memory[:, -self.n_states:], dtype=torch.float)

        # Compute loss between Q values of eval net & target net
        q_eval = self.eval_net(b_state).gather(1, b_action)                     # evaluate the Q values of the experiences, given the states & actions taken at that time
        q_next = self.target_net(b_next_state).detach()                         # detach from graph, don't backpropagate

        #====== code segment starts ======

        q_target = b_reward + self.gamma * q_next.max(1).values.unsqueeze(-1)   # compute the target Q values
        loss = self.loss_func(q_eval,q_target)
        #====== code segment ends ======

        # Backpropagation
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target network every few iterations (target_replace_iter), i.e. replace target net with eval net
        self.learn_step_counter += 1

        if self.learn_step_counter % self.target_replace_iter == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())

    def save_model(self):
        torch.save(self.eval_net.state_dict(), 'cartpole_dqn_model')

    def load_model(self):
        self.eval_net.load_state_dict(torch.load('cartpole_dqn_model'))

env = gym.make('CartPole-v0')
env = env.unwrapped # For cheating mode to access values hidden in the environment

# Environment parameters
n_actions = env.action_space.n
n_states = env.observation_space.shape[0]

#====== code segment starts ======

# Hyper parameters
n_hidden = 128
batch_size = 40
lr = 0.01                    # learning rate
epsilon = 0.1               # epsilon-greedy, factor to explore randomly
gamma = 0.9                 # reward discount factor
target_replace_iter = 100   # target network update frequency
memory_capacity = 3000

# Create DQN
dqn = DQN(n_states, n_actions, n_hidden, batch_size, lr, epsilon, gamma, target_replace_iter, memory_capacity)

#====== code segment ends ======

# Collect experience
all_rewards = []

for i_episode in range(N_EPISODES):
    rewards = 0 # accumulate rewards for each episode
    state = env.reset() # reset environment to initial state for each episode

    for t in range(EPISODE_LENGTH):
        env.render()

        #====== code segment starts ======

        # Agent takes action
        action = dqn.choose_action(state)                         # choose an action based on DQN
        next_state, actual_reward, done, info = env.step(action)   # do the action, get the reward
        reward = actual_reward

        #====== code segment ends ======

        ### Cheating part: modify the reward to speed up training process
        x, v, theta, omega = next_state
        r1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8                             # reward 1: the closer the cart is to the center, the better
        r2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5 # reward 2: the closer the pole is to the center, the better
        reward = r1 + r2

        #====== code segment starts ======

        # Keep the experience in memory
        dqn.store_transition(state, action, reward, next_state)

        # Accumulate reward
        rewards += actual_reward

        # If enough memory stored, agent learns from them via Q-learning
        if dqn.memory_counter > memory_capacity:
            dqn.learn()

        # Transition to next state
        state = next_state

        #====== code segment ends ======

        if done:
            print('Episode {} finished after {} timesteps, total rewards {}'.format(i_episode ,t+1, rewards))
            break
    all_rewards.append(rewards)

draw(all_rewards, "Cartpole DQN action reward")

dqn.save_model()

env.close()