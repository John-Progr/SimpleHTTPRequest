import itertools
import random
import argparse
import os

# Define available channels as a global constant
AVAILABLE_CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 36, 40, 44, 48, 149, 153, 157, 161, 165]

def load_ips(filename):
    """
    Loads IP addresses from a specified file.
    Each IP address should be on a new line.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"❌ Error: IP list file '{filename}' not found.")
    with open(filename, "r") as f:
        ips = [line.strip() for line in f if line.strip()]
    if not ips:
        raise ValueError(f"❌ Error: IP list file '{filename}' is empty or contains no valid IPs.")
    return ips

def get_all_non_empty_subsets(lst):
    """
    This function is no longer used in the current version, as commands
    now use individual channels, not subsets.
    Generates all non-empty subsets of a given list.
    Used for creating combinations of channels.
    """
    return [list(sub) for i in range(1, len(lst) + 1) for sub in itertools.combinations(lst, i)]

def generate_all_commands(ips, channels, min_path_len, max_path_len):
    """
    Generates a list of network commands based on IPs, channels, and path length constraints.
    Each command will now use only one channel.
    
    Args:
        ips (list): A list of available IP addresses.
        channels (list): A list of available communication channels.
        min_path_len (int): The minimum number of intermediate IPs in the path.
        max_path_len (int): The maximum number of intermediate IPs in the path.
    
    Returns:
        list: A list of generated command strings.
    """
    commands = []
    # No longer pre-calculating channel_subsets, as we only need individual channels

    # Ensure there are enough IPs for source, destination, and minimum path length
    if len(ips) < 2 + min_path_len:
        print(f"⚠️ Warning: Not enough IPs ({len(ips)}) to satisfy min_path_length ({min_path_len}). "
              "Some path lengths might not be generated.")

    # Iterate through all unique pairs of source and destination IPs (src ≠ dst)
    for src, dst in itertools.permutations(ips, 2):
        # Identify IPs that can be used as intermediate nodes (not src or dst)
        remaining_ips_for_path = [ip for ip in ips if ip not in (src, dst)]
        
        # Determine the effective maximum path length based on available remaining IPs
        effective_max_path_len = min(len(remaining_ips_for_path), max_path_len)

        # Iterate through possible path lengths, from min_path_len to effective_max_path_len
        # If min_path_len is greater than effective_max_path_len, this loop will not run,
        # which is correct as no valid paths can be formed.
        for path_len in range(min_path_len, effective_max_path_len + 1):
            # Generate all permutations of 'path_len' IPs from the remaining_ips_for_path
            for path in itertools.permutations(remaining_ips_for_path, path_len):
                # For each path, combine it with every *individual* channel
                # THIS IS THE KEY CHANGE: Iterating directly over 'channels'
                for channel in channels: 
                    # Format the command string to include only a single channel
                    cmd = f"from {src} to {dst} through {','.join(path)} channels {channel}" 
                    commands.append(cmd)
    return commands


def main():
    """
    Main function to parse arguments, generate commands, and write them to a file.
    """
    parser = argparse.ArgumentParser(
        description="Generate network commands with specified path lengths and channel combinations."
    )
    # Define command-line arguments
    parser.add_argument(
        "--ip_file",
        type=str,
        default="ips.txt",
        help="Path to the file containing IP addresses (one per line). Default: ips.txt"
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="commands.txt",
        help="Path to the output file where commands will be written. Default: commands.txt"
    )
    parser.add_argument(
        "--num_commands",
        type=int,
        default=100,
        help="The desired number of commands to output. The script will generate double this amount, "
             "shuffle, and then select this many. Default: 100"
    )
    parser.add_argument(
        "--min_path_length",
        type=int,
        default=0, # Default to 0 to allow direct connections (no 'through' path)
        help="Minimum number of intermediate IPs in the 'through' path. Default: 0"
    )
    parser.add_argument(
        "--max_path_length",
        type=int,
        default=2,
        help="Maximum number of intermediate IPs in the 'through' path. Default: 2"
    )

    args = parser.parse_args()

    # Validate argument values
    if args.min_path_length < 0:
        print("❌ Error: --min_path_length cannot be negative.")
        return
    if args.max_path_length < args.min_path_length:
        print("❌ Error: --max_path_length cannot be less than --min_path_length.")
        return
    if args.num_commands <= 0:
        print("❌ Error: --num_commands must be a positive integer.")
        return

    try:
        ips = load_ips(args.ip_file)
    except (FileNotFoundError, ValueError) as e:
        print(e)
        return

    # Minimum IPs required: 2 for src/dst + max_path_length for 'through'
    # If min_path_length is 0, we still need at least 2 IPs (src, dst).
    # If min_path_length > 0, we need at least 2 + min_path_length IPs.
    required_ips = 2 + args.max_path_length if args.max_path_length > 0 else 2
    if len(ips) < required_ips:
        print(f"❌ You need at least {required_ips} IPs in '{args.ip_file}' to satisfy the "
              f"max_path_length of {args.max_path_length}. Found {len(ips)} IPs.")
        return

    print(f"⏳ Generating up to {args.num_commands * 2} combinations...")
    # Generate double the requested number of commands to ensure good randomness after shuffling
    all_commands = generate_all_commands(ips, AVAILABLE_CHANNELS, args.min_path_length, args.max_path_length)
    
    # Shuffle the entire generated list
    random.shuffle(all_commands)
    
    # Select the desired number of commands, or fewer if not enough were generated
    selected_commands = all_commands[:args.num_commands]

    # Write the selected commands to the output file
    try:
        with open(args.output_file, "w") as f:
            for cmd in selected_commands:
                f.write(cmd + "\n")
        print(f"✅ Wrote {len(selected_commands)} commands to {args.output_file}")
    except IOError as e:
        print(f"❌ Error writing to file '{args.output_file}': {e}")


if __name__ == "__main__":
    main()
