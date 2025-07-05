import re
import requests
import csv
import os

API_ENDPOINT = "http://your.api.endpoint/measurements"
CSV_FILENAME = "responses.csv"

def parse_line(line):
    pattern = (
        r"from (?P<from>\d{1,3}(?:\.\d{1,3}){3}) "
        r"to (?P<to>\d{1,3}(?:\.\d{1,3}){3}) "
        r"through (?P<path>(?:\d{1,3}(?:\.\d{1,3}){3}(?:,)?)+) "
        r"channels (?P<channels>(?:\d+(?:,)?)+)"
    )
    match = re.search(pattern, line.strip())
    if match:
        return {
            "from": match.group("from"),
            "to": match.group("to"),
            "path": match.group("path").split(","),
            "channels": [int(ch) for ch in match.group("channels").split(",")]
        }
    return None

def send_request(data):
    response = requests.post(API_ENDPOINT, json=data)
    if response.status_code == 200:
        return response.text.strip()
    else:
        print(f"Request failed ({response.status_code}) for data: {data}")
        return None

def parse_csv_response(csv_text):
    lines = csv_text.splitlines()
    reader = csv.DictReader(lines)
    return list(reader)

def save_to_csv(rows):
    headers = [
        "Source",
        "Dest",
        "Path",
        "Channel",
        "Number of Intermediate Nodes",
        "Throughput"
    ]
    file_exists = os.path.isfile(CSV_FILENAME)
    with open(CSV_FILENAME, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

def process_entry(parsed):
    rows = []
    for channel in parsed["channels"]:
        request_data = {
            "from": parsed["from"],
            "to": parsed["to"],
            "path": parsed["path"],
            "channel": channel
        }

        print(f"Sending: {request_data}")
        csv_response = send_request(request_data)

        if not csv_response:
            continue

        csv_rows = parse_csv_response(csv_response)
        for row in csv_rows:
            rows.append({
                "Source": row["source"],
                "Dest": row["destination"],
                "Path": ",".join(parsed["path"]),
                "Channel": row["wireless_channel"],
                "Number of Intermediate Nodes": len(parsed["path"]),
                "Throughput": row["throughput"]
            })
    return rows

def run_from_txt():
    all_rows = []
    with open("commands.txt", "r") as file:
        for index, line in enumerate(file):
            parsed = parse_line(line)
            if not parsed:
                print(f"Failed to parse line {index}: {line.strip()}")
                continue
            all_rows.extend(process_entry(parsed))

    if all_rows:
        save_to_csv(all_rows)
        print(f"Saved {len(all_rows)} results to {CSV_FILENAME}")

def run_from_cli():
    print("\nExample format:")
    print("from 192.168.0.1 to 192.168.0.5 through 192.168.0.2,192.168.0.3 channels 1,6\n")
    
    while True:
        user_input = input("Enter measurement command (or 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            break

        parsed = parse_line(user_input)
        if not parsed:
            print("❌ Invalid format. Try again.")
            continue

        rows = process_entry(parsed)
        if rows:
            save_to_csv(rows)
            print(f"✅ Saved {len(rows)} row(s) to {CSV_FILENAME}")

def main():
    print("Select mode:\n1. CLI input\n2. Read from commands.txt")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        run_from_cli()
    elif choice == "2":
        run_from_txt()
    else:
        print("❌ Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
