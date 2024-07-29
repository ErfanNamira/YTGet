import subprocess
import os
import urllib.request
import json

# ANSI escape codes for colors
class Colors:
    LIGHT_RED = '\033[91m'
    LIGHT_CYAN = '\033[96m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_MAGENTA = '\033[95m'
    RESET = '\033[0m'

# Function to check internet connectivity using urllib
def check_internet_connectivity():
    try:
        response = urllib.request.urlopen('https://www.youtube.com', timeout=5)
        return response.status == 200
    except Exception:
        return False

# Function to get the latest version from GitHub
def get_latest_version():
    url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        latest_version = data['tag_name']
    return latest_version

# Function to download the latest yt-dlp executable
def download_latest_version(latest_version):
    download_url = f"https://github.com/yt-dlp/yt-dlp/releases/download/{latest_version}/yt-dlp.exe"
    with urllib.request.urlopen(download_url) as response, open("yt-dlp.exe", "wb") as out_file:
        out_file.write(response.read())

# Function to get the local version of yt-dlp
def get_local_version():
    if not os.path.exists('yt-dlp.exe'):
        return None
    result = subprocess.run(['yt-dlp.exe', '--version'], capture_output=True, text=True)
    local_version = result.stdout.strip()
    return local_version

# Function to fetch available formats for a given URL
def get_available_formats(url):
    result = subprocess.run(['yt-dlp.exe', '-F', url], capture_output=True, text=True)
    formats = result.stdout
    excluded_formats = ["sb2", "sb3", "sb1", "sb0", "drc", "18", "sb3 mhtml", "sb2 mhtml", "sb1 mhtml", "sb0 mhtml", "233 mp4", "234 mp4", "18  mp4"]
    excluded_lines = [
        "Extracting URL",
        "Downloading webpage",
        "Downloading ios player API JSON",
        "Downloading m3u8 information"
    ]
    lines = formats.splitlines()
    filtered_lines = [
        line for line in lines 
        if not any(ex_line in line for ex_line in excluded_lines) and not any(exf in line for exf in excluded_formats)
    ]
    return "\n".join(filtered_lines)

# Function to download video with the specified format
def download_video(url, format_code, download_path, max_retries=3):
    os.makedirs(download_path, exist_ok=True)
    retries = 0
    while retries < max_retries:
        result = subprocess.run(['yt-dlp.exe', '-f', format_code, url, '-o', os.path.join(download_path, '%(title)s.%(ext)s')])
        if result.returncode == 0:
            return True
        retries += 1
    return False

# Function to load configuration from a file
def load_config():
    if os.path.exists('YTGet_Conf.json'):
        with open('YTGet_Conf.json', 'r') as config_file:
            config = json.load(config_file)
        return config
    return {"download_path": None, "queue": [], "failed_downloads": []}

# Function to save configuration to a file
def save_config(config):
    with open('YTGet_Conf.json', 'w') as config_file:
        json.dump(config, config_file)

# Function to add a new download to the queue
def add_download_to_queue(url, format_code, config):
    config["queue"].append({"url": url, "format_code": format_code})
    save_config(config)

# Function to process the download queue
def process_queue(config):
    queue_copy = config["queue"][:]
    for item in queue_copy:
        url = item["url"]
        format_code = item["format_code"]
        download_path = config["download_path"] or os.getcwd()
        print(f"{Colors.LIGHT_GREEN}Starting download for {url}...{Colors.RESET}")
        if download_video(url, format_code, download_path):
            print(f"{Colors.LIGHT_GREEN}Download completed for {url}.{Colors.RESET}")
            config["queue"].remove(item)
        else:
            print(f"{Colors.LIGHT_RED}Download failed for {url}. Adding to failed downloads.{Colors.RESET}")
            config["failed_downloads"].append(item)
            config["queue"].remove(item)
        save_config(config)

def main():
    print(f"{Colors.LIGHT_RED}Welcome to YTGet 1.0.2{Colors.RESET}")

    # Check internet connectivity
    while True:
        print(f"{Colors.LIGHT_CYAN}Checking internet connectivity...{Colors.RESET}")
        if not check_internet_connectivity():
            print(f"{Colors.LIGHT_RED}No internet connection detected. Please check your connection and press Enter to retry.{Colors.RESET}")
            input()
        else:
            break

    # Check for updates
    print(f"{Colors.LIGHT_CYAN}Checking for updates...{Colors.RESET}")
    latest_version = get_latest_version()
    local_version = get_local_version()

    if local_version is None:
        print(f"{Colors.LIGHT_RED}yt-dlp.exe not found. Downloading the latest version...{Colors.RESET}")
        download_latest_version(latest_version)
        print(f"{Colors.LIGHT_GREEN}yt-dlp.exe has been downloaded and updated to version {latest_version}.{Colors.RESET}")
    elif latest_version != local_version:
        print(f"{Colors.LIGHT_RED}A new version of yt-dlp is available: {latest_version} (current version: {local_version}){Colors.RESET}")
        update = input("Do you want to update yt-dlp? (y/n): ")
        if update.lower() == 'y':
            print(f"{Colors.LIGHT_CYAN}Downloading the latest version of yt-dlp...{Colors.RESET}")
            download_latest_version(latest_version)
            print(f"{Colors.LIGHT_GREEN}Update completed. You now have the latest version: {latest_version}.{Colors.RESET}")
        else:
            print(f"{Colors.LIGHT_RED}Skipping update.{Colors.RESET}")
    else:
        print(f"{Colors.LIGHT_GREEN}You already have the latest version: {latest_version}{Colors.RESET}")

    config = load_config()

    try:
        while True:
            print(f"{Colors.LIGHT_BLUE}\nMenu:\n1. Download A Single YouTube Video\n2. Start Download Queue\n3. Exit\n{Colors.RESET}")
            choice = input("Enter your choice: ")

            if choice == '1':
                url = input(f"{Colors.LIGHT_YELLOW}Enter YouTube URL: {Colors.RESET}")
                print(f"{Colors.LIGHT_BLUE}Fetching available formats...{Colors.RESET}")
                available_formats = get_available_formats(url)

                format_lines = available_formats.split('\n')
                for i, line in enumerate(format_lines):
                    if line.startswith("[info] Available formats for"):
                        format_lines[i] = f"{Colors.LIGHT_YELLOW}{line}"

                print("\n".join(format_lines))
                format_code = input(f"{Colors.LIGHT_BLUE}Enter format code to download (e.g., 251 or 251+271): {Colors.RESET}")

                download_path = config["download_path"]
                if download_path:
                    change_path = input(f"{Colors.LIGHT_CYAN}Current download path is '{download_path}'. Do you want to change it? (y/n): {Colors.RESET}")
                    if change_path.lower() == 'y':
                        download_path = input(f"{Colors.LIGHT_YELLOW}Enter new download path: {Colors.RESET}")
                        config["download_path"] = download_path
                        save_config(config)
                else:
                    use_default_path = input(f"{Colors.LIGHT_CYAN}No download path set. Do you want to enter a download path? (y/n): {Colors.RESET}")
                    if use_default_path.lower() == 'y':
                        download_path = input(f"{Colors.LIGHT_YELLOW}Enter download path: {Colors.RESET}")
                        config["download_path"] = download_path
                        save_config(config)
                    else:
                        download_path = os.getcwd()

                queue_or_immediate = input(f"{Colors.LIGHT_CYAN}Do you want to add this download to the queue or start immediately? (q/i): {Colors.RESET}")
                if queue_or_immediate.lower() == 'q':
                    add_download_to_queue(url, format_code, config)
                    print(f"{Colors.LIGHT_GREEN}Added to download queue.{Colors.RESET}")
                else:
                    print(f"{Colors.LIGHT_GREEN}Downloading Started...{Colors.RESET}")
                    if download_video(url, format_code, download_path):
                        print(f"{Colors.LIGHT_GREEN}Download finished.{Colors.RESET}")
                    else:
                        print(f"{Colors.LIGHT_RED}Download failed. Adding to failed downloads.{Colors.RESET}")
                        config["failed_downloads"].append({"url": url, "format_code": format_code})
                    save_config(config)

            elif choice == '2':
                print(f"{Colors.LIGHT_CYAN}Starting download queue...{Colors.RESET}")
                process_queue(config)
                print(f"{Colors.LIGHT_GREEN}Download queue processing completed.{Colors.RESET}")

            elif choice == '3':
                print(f"{Colors.LIGHT_RED}Exiting program. Goodbye!{Colors.RESET}")
                break
    except KeyboardInterrupt:
        print(f"\n{Colors.LIGHT_RED}Program interrupted. Exiting...{Colors.RESET}")

if __name__ == "__main__":
    main()
