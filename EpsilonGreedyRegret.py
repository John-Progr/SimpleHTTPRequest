import numpy as np
import matplotlib.pyplot as plt

class EpsilonGreedy:
    def __init__(self, n_arms, epsilon, true_means):
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.true_means = true_means  # Needed to calculate regret, ground truth ( needed for regret calculation)
        self.counts = np.zeros(n_arms)   # Number of times each arm is pulled
        self.values = np.zeros(n_arms)   # Estimated values of each arm
        self.regret_history = []         # Track cumulative regret, list of cumulative regret at each step.
        self.rewards_history = []        # Track rewards, list of all observed rewards.
        self.chosen_arms = []            # Track chosen arms, records which arms were picked
        self.cumulative_regret = 0       # Running total, running sum of target

    def select_arm(self):
        """Choose an arm (explore or exploit)."""
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.n_arms)   # Explore
        else:
            return np.argmax(self.values)           # Exploit best so far

    def update(self, chosen_arm, reward):
        """Update estimates and regret tracking."""
        # Update counts and values (incremental mean)
        self.counts[chosen_arm] += 1
        n = self.counts[chosen_arm]
        value = self.values[chosen_arm]
        self.values[chosen_arm] = value + (reward - value) / n

        # Compute regret = best possible mean - chosen arm's mean
        optimal_mean = max(self.true_means)
        regret = optimal_mean - self.true_means[chosen_arm]
        self.cumulative_regret += regret

        # Store history
        self.regret_history.append(self.cumulative_regret)
        self.rewards_history.append(reward)
        self.chosen_arms.append(chosen_arm)


# -------------------------
# Show Case / Simulation
# -------------------------

n_arms = 13          # Number of channels (arms)
epsilon = 0.1        # 10% exploration
n_trials = 1000      # Number of iterations

# Define the "true" mean throughput of each channel
true_means = np.linspace(5, 50, n_arms)  # arms 0..9 have means 1..10

# Generate noisy rewards for simulation
rewards = np.random.normal(loc=true_means[:, None], scale=1.0, size=(n_arms, n_trials))

# Initialize agent
agent = EpsilonGreedy(n_arms, epsilon, true_means)

# Run trials
total_reward = 0
for t in range(n_trials):
    arm = agent.select_arm()
    reward = rewards[arm, t]   # in real system → API measurement
    agent.update(arm, reward)
    total_reward += reward

# -------------------------
# Results
# -------------------------

print("Total Reward: ", round(total_reward, 2))
print("Estimated Values: ", np.round(agent.values, 2))
print("Arm Selection Counts: ", agent.counts.astype(int))
print("Best Arm (True):", np.argmax(true_means))
print("Best Arm (Learned):", np.argmax(agent.values))
print("Final Cumulative Regret:", round(agent.cumulative_regret, 2))

# -------------------------
# Visualization
# -------------------------

fig, axs = plt.subplots(3, 1, figsize=(12, 14))

# 1. Average reward
avg_reward = np.cumsum(agent.rewards_history) / (np.arange(1, n_trials+1))
axs[0].plot(avg_reward, label="Average Reward")
axs[0].axhline(max(true_means), color="red", linestyle="--", label="Optimal Mean Reward")
axs[0].set_title("Average Reward vs Optimal")
axs[0].set_xlabel("Iteration")
axs[0].set_ylabel("Reward")
axs[0].legend()

# 2. Cumulative regret
axs[1].plot(agent.regret_history, color="orange")
axs[1].set_title("Cumulative Regret")
axs[1].set_xlabel("Iteration")
axs[1].set_ylabel("Regret")

# 3. Arm selection counts
axs[2].bar(range(n_arms), agent.counts, tick_label=[f"Ch {i}" for i in range(n_arms)])
axs[2].set_title("Channel Selection Counts")
axs[2].set_xlabel("Channel")
axs[2].set_ylabel("Times Chosen")

plt.tight_layout()
plt.show()

