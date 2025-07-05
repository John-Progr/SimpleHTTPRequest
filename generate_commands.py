import random

IP_LIST_FILE = "ips.txt"
OUTPUT_FILE = "commands.txt"

NUM_COMMANDS = 20  # Number of lines to generate
MAX_PATH_LENGTH = 4  # Max number of intermediate nodes per route
AVAILABLE_CHANNELS = [1, 6, 11]  # Customize as needed


def load_ips(filename):
    with open(filename, "r") as f:
        ips = [line.strip() for line in f if line.strip()]
    return ips


def generate_command(ips, channels):
    while True:
        src, dst = random.sample(ips, 2)
        remaining_ips = [ip for ip in ips if ip not in (src, dst)]
        if not remaining_ips:
            continue  # Try again

        path_len = random.randint(1, min(len(remaining_ips), MAX_PATH_LENGTH))
        path = random.sample(remaining_ips, path_len)
        used_channels = random.sample(channels, random.randint(1, len(channels)))

        return f"from {src} to {dst} through {','.join(path)} channels {','.join(map(str, used_channels))}"


def main():
    ips = load_ips(IP_LIST_FILE)
    if len(ips) < 3:
        print("❌ You need at least 3 IPs in ips.txt")
        return

    with open(OUTPUT_FILE, "w") as f:
        for _ in range(NUM_COMMANDS):
            command = generate_command(ips, AVAILABLE_CHANNELS)
            f.write(command + "\n")

    print(f"✅ Generated {NUM_COMMANDS} commands in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
