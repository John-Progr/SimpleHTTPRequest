import numpy as np
import matplotlib.pyplot as plt

class EpsilonGreedy:
    def __init__(self, n_arms, epsilon):
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.counts = np.zeros(n_arms)   # Number of times each arm is pulled, basically how often each channel is used 
        self.values = np.zeros(n_arms)   # Estimated values of each arm, basically estimated throughput per channel

    def select_arm(self):
        """Choose an arm (explore or exploit)."""
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.n_arms)   # Explore
        else:
            return np.argmax(self.values)           # Exploit best so far

    def update(self, chosen_arm, reward):
        """Update estimated value of the chosen arm using incremental mean."""
        self.counts[chosen_arm] += 1
        n = self.counts[chosen_arm]
        value = self.values[chosen_arm]
        self.values[chosen_arm] = value + (reward - value) / n


# -------------------------
# Show Case / Simulation
# -------------------------

n_arms = 13                       # Wi-Fi channels 1 to 13
channels = list(range(1, 14))     # channel IDs

epsilon = 0.1
n_trials = 1000

# Simulated "true mean throughput" for each channel (random Mbps between 5–50)
true_means = np.random.uniform(5, 50, n_arms)

# Simulated reward samples with noise
rewards = np.random.normal(loc=true_means[:, None], scale=3.0, size=(n_arms, n_trials))

agent = EpsilonGreedy(n_arms, epsilon)
total_reward = 0
reward_history = []
chosen_arms = []

for t in range(n_trials):
    arm = agent.select_arm()
    reward = rewards[arm, t]   # In practice, this would come from API
    agent.update(arm, reward)
    total_reward += reward

    reward_history.append(reward)
    chosen_arms.append(arm)

print("Channels:", channels)
print("True Mean Throughputs (Mbps):", np.round(true_means, 2))
print("Estimated Values:", np.round(agent.values, 2))
print("Arm Selection Counts:", agent.counts.astype(int))
print("Best Channel (True):", channels[np.argmax(true_means)])
print("Best Channel (Learned):", channels[np.argmax(agent.values)])

# -------------------------
# Visualization
# -------------------------

plt.figure(figsize=(12, 6))
plt.plot(np.cumsum(reward_history) / (np.arange(1, n_trials+1)), label="Average Reward")
plt.axhline(max(true_means), color="red", linestyle="--", label="Optimal Mean Reward")
plt.xlabel("Iteration")
plt.ylabel("Average Reward (Mbps)")
plt.title("Epsilon-Greedy Performance on Channels 1–13")
plt.legend()
plt.show()

