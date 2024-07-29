# YTGet.py
__version__ = '1.0.5'

import subprocess
import os
import urllib.request
import json
import time
import msvcrt
import sys

# ANSI escape codes for colors
class Colors:
    LIGHT_RED = '\033[91m'
    LIGHT_CYAN = '\033[96m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_MAGENTA = '\033[95m'
    RESET = '\033[0m'

# Utility function to print messages with color
def print_colored(message, color):
    print(f"{color}{message}{Colors.RESET}")

# Function to check internet connectivity using urllib
def check_internet_connectivity():
    try:
        response = urllib.request.urlopen('https://www.youtube.com', timeout=5)
        return response.status == 200
    except Exception as e:
        print_colored(f"Error checking internet connectivity: {e}", Colors.LIGHT_RED)
        return False

# Function to get the latest version from GitHub for YTGet.py
def get_latest_version_youtube():
    url = "https://api.github.com/repos/ErfanNamira/YTGet/releases/latest"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data['tag_name'].strip()
    except Exception as e:
        print_colored(f"Error fetching latest version: {e}", Colors.LIGHT_RED)
        return None

# Function to download the latest YTGet.py
def download_latest_version_youtube(latest_version):
    download_url = f"https://github.com/ErfanNamira/YTGet/releases/download/{latest_version}/YTGet.py"
    try:
        with urllib.request.urlopen(download_url) as response, open("YTGet_new.py", "wb") as out_file:
            out_file.write(response.read())
    except Exception as e:
        print_colored(f"Error downloading latest version: {e}", Colors.LIGHT_RED)

# Function to get the local version of YTGet
def get_local_version_youtube():
    try:
        with open('YTGet.py', 'r') as file:
            for line in file:
                if line.strip().startswith('__version__'):
                    return line.strip().split('=')[1].strip().strip("'")
    except FileNotFoundError:
        return None
    except Exception as e:
        print_colored(f"Error reading local version: {e}", Colors.LIGHT_RED)
    return None

# Function to update YTGet.py and restart
def update_and_restart_youtube():
    latest_version = get_latest_version_youtube()
    if latest_version:
        print_colored("Downloading the latest version of YTGet...", Colors.LIGHT_CYAN)
        download_latest_version_youtube(latest_version)
        print_colored("Update completed. Restart the program to access the newest version.", Colors.LIGHT_GREEN)
        os.rename('YTGet.py', 'YTGet_old.py')
        os.rename('YTGet_new.py', 'YTGet.py')
    else:
        print_colored("Update failed. Latest version could not be fetched.", Colors.LIGHT_RED)

# Function to get the latest version from GitHub for yt-dlp
def get_latest_version_yt_dlp():
    url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data['tag_name']
    except Exception as e:
        print_colored(f"Error fetching yt-dlp latest version: {e}", Colors.LIGHT_RED)
        return None

# Function to download the latest yt-dlp executable
def download_latest_version_yt_dlp(latest_version):
    download_url = f"https://github.com/yt-dlp/yt-dlp/releases/download/{latest_version}/yt-dlp.exe"
    try:
        with urllib.request.urlopen(download_url) as response, open("yt-dlp.exe", "wb") as out_file:
            out_file.write(response.read())
    except Exception as e:
        print_colored(f"Error downloading yt-dlp: {e}", Colors.LIGHT_RED)

# Function to get the local version of yt-dlp
def get_local_version_yt_dlp():
    if not os.path.exists('yt-dlp.exe'):
        return None
    result = subprocess.run(['yt-dlp.exe', '--version'], capture_output=True, text=True)
    return result.stdout.strip()

# Function to fetch available formats for a given URL
def get_available_formats(url):
    try:
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
    except Exception as e:
        print_colored(f"Error fetching available formats: {e}", Colors.LIGHT_RED)
        return ""

# Function to download video with the specified format
def download_video(url, format_code, download_path, max_retries=10):
    os.makedirs(download_path, exist_ok=True)
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(['yt-dlp.exe', '-f', format_code, url, '-o', os.path.join(download_path, '%(title)s.%(ext)s')])
            if result.returncode == 0:
                return True
        except Exception as e:
            print_colored(f"Error during video download: {e}", Colors.LIGHT_RED)
        retries += 1
    return False

# Function to load configuration from a file
def load_config():
    if os.path.exists('YTGet_Conf.json'):
        try:
            with open('YTGet_Conf.json', 'r') as config_file:
                return json.load(config_file)
        except Exception as e:
            print_colored(f"Error loading configuration: {e}", Colors.LIGHT_RED)
    return {"download_path": None, "queue": [], "failed_downloads": []}

# Function to save configuration to a file
def save_config(config):
    try:
        with open('YTGet_Conf.json', 'w') as config_file:
            json.dump(config, config_file)
    except Exception as e:
        print_colored(f"Error saving configuration: {e}", Colors.LIGHT_RED)

# Function to add a new download to the queue
def add_download_to_queue(url, format_code, download_path, config):
    config["queue"].append({"url": url, "format_code": format_code, "download_path": download_path})
    save_config(config)

# Function to process the download queue
def process_queue(config):
    queue_copy = config["queue"][:]
    for item in queue_copy:
        url = item["url"]
        format_code = item["format_code"]
        download_path = item["download_path"] or config["download_path"] or os.getcwd()
        print(f"{Colors.LIGHT_GREEN}Starting download for {url}...{Colors.RESET}")
        if download_video(url, format_code, download_path):
            print(f"{Colors.LIGHT_GREEN}Download completed for {url}.{Colors.RESET}")
            config["queue"].remove(item)
        else:
            print(f"{Colors.LIGHT_RED}Download failed for {url}. Adding to failed downloads.{Colors.RESET}")
            config["failed_downloads"].append(item)
            config["queue"].remove(item)
        save_config(config)

def shutdown_or_sleep(option):
    for i in range(60, 0, -1):
        print(f"{Colors.LIGHT_RED}System will {option} in {i} seconds. Press 'E' to cancel.{Colors.RESET}", end="\r")
        if cancel_shutdown_or_sleep():
            print(f"{Colors.LIGHT_GREEN}{option.capitalize()} canceled.{Colors.RESET}")
            return
        time.sleep(1)

    if option == "shutdown":
        os.system("shutdown /s /t 0")
    elif option == "sleep":
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def cancel_shutdown_or_sleep():
    if msvcrt.kbhit() and msvcrt.getch().decode('utf-8').lower() == 'e':
        return True
    return False

def menu():
    while True:
        print_colored("\nOnce the download queue has finished, what would you like to do next?\n1. Keep system idle\n2. Shut down system after 60 seconds\n3. Sleep system after 60 seconds", Colors.LIGHT_BLUE)
        choice = input("Enter your choice: ")

        if choice == '1':
            return "idle"
        elif choice == '2':
            return "shutdown"
        elif choice == '3':
            return "sleep"
        else:
            print_colored("Invalid choice. Please try again.", Colors.LIGHT_RED)

def main():
    print_colored(f"Welcome to YTGet {__version__}", Colors.LIGHT_RED)

    # Check internet connectivity
    while not check_internet_connectivity():
        print_colored("No internet connection detected. Please check your connection and press Enter to retry.", Colors.LIGHT_RED)
        input()

    # Check for updates
    print_colored("Checking for updates...", Colors.LIGHT_CYAN)
    latest_version_youtube = get_latest_version_youtube()
    local_version_youtube = get_local_version_youtube()

    if local_version_youtube is None:
        if latest_version_youtube:
            print_colored(f"YTGet.py not found. Downloading the latest version...", Colors.LIGHT_RED)
            download_latest_version_youtube(latest_version_youtube)
            print_colored(f"YTGet.py has been downloaded and updated to version {latest_version_youtube}.", Colors.LIGHT_GREEN)
        else:
            print_colored("Cannot fetch latest version. Update aborted.", Colors.LIGHT_RED)
    elif latest_version_youtube != local_version_youtube:
        print_colored(f"A new version of YTGet is available: {latest_version_youtube} (current version: {local_version_youtube})", Colors.LIGHT_RED)
        update = input("Do you want to update YTGet? (y/n): ")
        if update.lower() == 'y':
            update_and_restart_youtube()
        else:
            print_colored("Skipping update.", Colors.LIGHT_RED)
    else:
        print_colored(f"You already have the latest version: {latest_version_youtube}", Colors.LIGHT_GREEN)

    # Update yt-dlp if necessary
    latest_version_yt_dlp = get_latest_version_yt_dlp()
    local_version_yt_dlp = get_local_version_yt_dlp()

    if local_version_yt_dlp is None:
        if latest_version_yt_dlp:
            print_colored(f"yt-dlp not found. Downloading the latest version...", Colors.LIGHT_RED)
            download_latest_version_yt_dlp(latest_version_yt_dlp)
            print_colored(f"yt-dlp has been downloaded and updated to version {latest_version_yt_dlp}.", Colors.LIGHT_GREEN)
        else:
            print_colored("Cannot fetch yt-dlp latest version. Update aborted.", Colors.LIGHT_RED)
    elif latest_version_yt_dlp != local_version_yt_dlp:
        print_colored(f"A new version of yt-dlp is available: {latest_version_yt_dlp} (current version: {local_version_yt_dlp})", Colors.LIGHT_RED)
        update = input("Do you want to update yt-dlp? (y/n): ")
        if update.lower() == 'y':
            download_latest_version_yt_dlp(latest_version_yt_dlp)
            print_colored("yt-dlp has been updated.", Colors.LIGHT_GREEN)
        else:
            print_colored("Skipping update.", Colors.LIGHT_RED)
    else:
        print_colored(f"You already have the latest version of yt-dlp: {latest_version_yt_dlp}", Colors.LIGHT_GREEN)

    config = load_config()

    try:
        while True:
            print_colored("\nMenu:\n1. Download A Single YouTube Video\n2. Start Download Queue\n3. Exit", Colors.LIGHT_BLUE)
            choice = input("Enter your choice: ")

            if choice == '1':
                url = input(f"{Colors.LIGHT_CYAN}Enter YouTube URL: {Colors.RESET}")
                print_colored("Fetching available formats...", Colors.LIGHT_CYAN)
                available_formats = get_available_formats(url)

                if not available_formats:
                    print_colored("Failed to fetch formats. Please try again later.", Colors.LIGHT_RED)
                    continue

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
                    add_download_to_queue(url, format_code, download_path, config)
                    print_colored("Added to download queue.", Colors.LIGHT_GREEN)
                else:
                    print_colored("Downloading Started...", Colors.LIGHT_GREEN)
                    if download_video(url, format_code, download_path):
                        print_colored("Download finished.", Colors.LIGHT_GREEN)
                    else:
                        print_colored("Download failed. Adding to failed downloads.", Colors.LIGHT_RED)
                        config["failed_downloads"].append({"url": url, "format_code": format_code})
                    save_config(config)

            elif choice == '2':
                post_queue_action = menu()
                print_colored("Starting download queue...", Colors.LIGHT_CYAN)
                process_queue(config)
                print_colored("Download queue processing completed.", Colors.LIGHT_GREEN)
                if post_queue_action == "idle":
                    print_colored("System will remain idle.", Colors.LIGHT_GREEN)
                elif post_queue_action == "shutdown":
                    shutdown_or_sleep("shutdown")
                elif post_queue_action == "sleep":
                    shutdown_or_sleep("sleep")

            elif choice == '3':
                print_colored("Exiting program. Goodbye!", Colors.LIGHT_RED)
                break
    except KeyboardInterrupt:
        print_colored("Program interrupted. Exiting...", Colors.LIGHT_RED)

if __name__ == "__main__":
    main()
