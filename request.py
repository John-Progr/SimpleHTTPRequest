import re
import requests

# Change this to your actual API endpoint
API_ENDPOINT = "http://your.api.endpoint/measurements"

def parse_line(line):
    pattern = (
        r"from (?P<from>\d{1,3}(?:\.\d{1,3}){3}) "
        r"to (?P<to>\d{1,3}(?:\.\d{1,3}){3}) "
        r"through (?P<path>(?:\d{1,3}(?:\.\d{1,3}){3}(?:,)?)+) "
        r"with olsr (?P<olsr>on|off)"
    )
    match = re.search(pattern, line.strip())
    if match:
        return {
            "from": match.group("from"),
            "to": match.group("to"),
            "path": match.group("path").split(","),
            "olsr": match.group("olsr") == "on"
        }
    return None

def send_request(data, index):
    response = requests.post(API_ENDPOINT, json=data)
    if response.status_code == 200:
        filename = f"response_{index}.bin"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Saved response to {filename}")
    else:
        print(f"Failed to send request for {data}, status code: {response.status_code}")

def main():
    with open("commands.txt", "r") as file:
        for index, line in enumerate(file):
            parsed = parse_line(line)
            if parsed:
                send_request(parsed, index)
            else:
                print(f"Failed to parse line: {line}")

if __name__ == "__main__":
    main()
