import subprocess
import os
import urllib.request
import json
import time
import sys
from urllib.error import HTTPError, URLError

__version__ = '1.1.8'

# ANSI escape codes for colors
class Colors:
    LIGHT_RED = '\033[91m'
    LIGHT_CYAN = '\033[96m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_MAGENTA = '\033[95m'
    LIGHT_PINK = '\033[38;5;217m'
    PASTEL_BLUE = '\033[38;5;159m'
    PASTEL_PURPLE = '\033[38;5;183m'
    PASTEL_YELLOW = '\033[38;5;229m'
    PASTEL_ORANGE = '\033[38;5;215m'
    GRAY = '\033[90m'        
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Utility function to print messages with color
def print_colored(message, color):
    print(f"{color}{message}{Colors.RESET}")

# Function to check internet connectivity using urllib
def check_internet_connectivity():
    try:
        response = urllib.request.urlopen('https://www.youtube.com', timeout=5)
        return response.status == 200
    except (HTTPError, URLError) as e:
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
        excluded_formats = ["sb2", "sb3", "sb1", "sb0", "drc", "18", "sb3 mhtml", "sb2 mhtml", "sb1 mhtml", "sb0 mhtml", "233 mp4", "234 mp4", "18  mp4", "233", "234"]
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
        return f"{Colors.LIGHT_YELLOW}\n".join(filtered_lines) + Colors.RESET
    except Exception as e:
        print_colored(f"Error fetching available formats: {e}", Colors.LIGHT_RED)
        return ""

# Function to download video with the specified format
def download_video(url, format_code, download_path, max_retries=10):
    if not url or not format_code or not download_path:
        print_colored("URL, format code, or download path cannot be empty.", Colors.LIGHT_RED)
        return False

    os.makedirs(download_path, exist_ok=True)
    retries = 0

    # Check if cookies.txt exists and set the command accordingly
    cookie_file = 'cookies.txt'
    if os.path.exists(cookie_file):
        cookie_option = ['--cookies', cookie_file]
    else:
        cookie_option = []

    while retries < max_retries:
        try:
            # Include the cookies option in the yt-dlp command
            result = subprocess.run(['yt-dlp.exe', '-f', format_code, url, '-o', os.path.join(download_path, '%(title)s.%(ext)s')] + cookie_option)
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
            json.dump(config, config_file, indent=4)
    except Exception as e:
        print_colored(f"Error saving configuration: {e}", Colors.LIGHT_RED)

# Function to add a new download to the queue
def add_download_to_queue(url, format_code, download_path, config):
    config["queue"].append({"url": url, "format_code": format_code, "download_path": download_path})
    save_config(config)

# Function to process the download queue
def process_queue(config):
    if not config["queue"]:
        print_colored("Queue is empty.", Colors.LIGHT_YELLOW)
        return
    
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

# Function to fetch playlist videos
def fetch_playlist_videos(playlist_url):
    try:
        result = subprocess.run(['yt-dlp.exe', '--flat-playlist', '-j', playlist_url], capture_output=True, text=True)
        video_urls = []
        for line in result.stdout.splitlines():
            video_data = json.loads(line)
            video_urls.append(f"https://www.youtube.com/watch?v={video_data['id']}")
        return video_urls
    except Exception as e:
        print_colored(f"Error fetching playlist videos: {e}", Colors.LIGHT_RED)
        return []

# Function to download the best quality (audio+video) for each video in a playlist
def download_playlist_best_quality(playlist_url, download_path):
    video_urls = fetch_playlist_videos(playlist_url)
    for video_url in video_urls:
        format_code = 'bestvideo+bestaudio/best'
        if not download_video(video_url, format_code, download_path):
            print_colored(f"Failed to download best quality for {video_url}.", Colors.LIGHT_RED)

# Function to download the best audio for each video in a playlist
def download_playlist_best_audio(playlist_url, download_path):
    video_urls = fetch_playlist_videos(playlist_url)
    for video_url in video_urls:
        format_code = 'bestaudio/best'
        if not download_video(video_url, format_code, download_path):
            print_colored(f"Failed to download audio for {video_url}.", Colors.LIGHT_RED)
# Function to Update yt-dlp & YTGet
def handle_update_youtube():
    latest_version_youtube = get_latest_version_youtube()
    local_version_youtube = get_local_version_youtube()

    # Skip update if rate limit exceeded
    if latest_version_youtube is None and "403" in str(latest_version_youtube):
        print_colored("Rate limit exceeded. Skipping YTGet update check.", Colors.LIGHT_RED)
        return  # Skip the rest of the update logic

    if local_version_youtube is None:
        if latest_version_youtube:
            print_colored(f"YTGet.py not found. Downloading the latest version...", Colors.LIGHT_RED)
            download_latest_version_youtube(latest_version_youtube)
            print_colored(f"YTGet.py has been downloaded and updated to version {latest_version_youtube}.", Colors.LIGHT_GREEN)
        else:
            print_colored("Cannot fetch latest version. Update aborted.", Colors.LIGHT_RED)
    elif latest_version_youtube != local_version_youtube:
        print_colored(f"A new version of YTGet is available: {latest_version_youtube} (current version: {local_version_youtube})", Colors.LIGHT_RED)
        print_colored("Skipping update due to rate limit.", Colors.LIGHT_RED)
    else:
        print_colored(f"You already have the latest version: {latest_version_youtube}", Colors.LIGHT_GREEN)

def handle_update_yt_dlp():
    latest_version_yt_dlp = get_latest_version_yt_dlp()
    local_version_yt_dlp = get_local_version_yt_dlp()

    # Skip update if rate limit exceeded
    if latest_version_yt_dlp is None and "403" in str(latest_version_yt_dlp):
        print_colored("Rate limit exceeded. Skipping yt-dlp update check.", Colors.LIGHT_RED)
        return  # Skip the rest of the update logic

    if local_version_yt_dlp is None:
        if latest_version_yt_dlp:
            print_colored(f"yt-dlp not found. Downloading the latest version...", Colors.LIGHT_RED)
            download_latest_version_yt_dlp(latest_version_yt_dlp)
            print_colored(f"yt-dlp has been downloaded and updated to version {latest_version_yt_dlp}.", Colors.LIGHT_GREEN)
        else:
            print_colored("Cannot fetch yt-dlp latest version. Update aborted.", Colors.LIGHT_RED)
    elif latest_version_yt_dlp != local_version_yt_dlp:
        print_colored(f"A new version of yt-dlp is available: {latest_version_yt_dlp} (current version: {local_version_yt_dlp})", Colors.LIGHT_RED)
        print_colored("Skipping update due to rate limit.", Colors.LIGHT_RED)
    else:
        print_colored(f"You already have the latest version of yt-dlp: {latest_version_yt_dlp}", Colors.LIGHT_GREEN)

def print_menu():
    print(f"{Colors.LIGHT_PINK}========== YTGet Main Menu =========={Colors.RESET}")
    print(f"{Colors.LIGHT_RED}1. Download A Specific Format{Colors.RESET}")
    print(f"{Colors.LIGHT_PINK}============ Best Format ============{Colors.RESET}")
    print(f"{Colors.PASTEL_BLUE}2. Download Best Audio Only{Colors.RESET}")
    print(f"{Colors.PASTEL_BLUE}3. Download Best Quality (Audio+Video){Colors.RESET}")
    print(f"{Colors.LIGHT_PINK}======== Download Playlists ========={Colors.RESET}")
    print(f"{Colors.PASTEL_PURPLE}4. Download Playlist Best Audio{Colors.RESET}")
    print(f"{Colors.PASTEL_PURPLE}5. Download Playlist Best Quality (Audio+Video){Colors.RESET}")
    print(f"{Colors.LIGHT_PINK}=============== Queue ==============={Colors.RESET}")
    print(f"{Colors.PASTEL_ORANGE}6. Start Download Queue{Colors.RESET}")
    print(f"{Colors.LIGHT_PINK}=============== Update =============={Colors.RESET}")
    print(f"{Colors.PASTEL_YELLOW}7. Check & Update YTGet{Colors.RESET}")
    print(f"{Colors.PASTEL_YELLOW}8. Check & Update yt-dlp{Colors.RESET}")
    print(f"{Colors.WHITE}9. Exit{Colors.RESET}")

def main():
    while not check_internet_connectivity():
        print_colored("No internet connection detected. Please check your connection and press Enter to retry.", Colors.LIGHT_RED)
        input()

    print_colored("Checking for updates...", Colors.LIGHT_CYAN)
    handle_update_youtube()
    handle_update_yt_dlp()

    config = load_config()

    while True:
        print_menu()
        choice = input(f"{Colors.LIGHT_CYAN}Enter your choice: {Colors.RESET}")

        if choice == '1':
            url = input(f"{Colors.LIGHT_CYAN}Enter the video URL: {Colors.RESET}")
            formats = get_available_formats(url)
            print(formats)
            format_code = input(f"{Colors.LIGHT_CYAN}Enter the format code to download: {Colors.RESET}")
            download_path = input(f"{Colors.LIGHT_CYAN}Enter the download path (leave empty for current directory): {Colors.RESET}")
            if not download_path:
                download_path = os.getcwd()
            action = input(f"{Colors.LIGHT_CYAN}Do you want to add this download to the queue or start immediately? (q/i): {Colors.RESET}")
            if action == 'i':
                download_video(url, format_code, download_path)
            else:
                add_download_to_queue(url, format_code, download_path, config)
                print_colored("Added to download queue.", Colors.LIGHT_GREEN)
        elif choice == '2':
            url = input(f"{Colors.LIGHT_CYAN}Enter the video URL: {Colors.RESET}")
            download_path = input(f"{Colors.LIGHT_CYAN}Enter the download path (leave empty for current directory): {Colors.RESET}")
            if not download_path:
                download_path = os.getcwd()
            action = input(f"{Colors.LIGHT_CYAN}Do you want to add this download to the queue or start immediately? (q/i): {Colors.RESET}")
            if action == 'i':
                download_video(url, 'bestaudio/best', download_path)
            else:
                add_download_to_queue(url, 'bestaudio/best', download_path, config)
                print_colored("Added to download queue.", Colors.LIGHT_GREEN)
        elif choice == '3':
            url = input(f"{Colors.LIGHT_CYAN}Enter the video URL: {Colors.RESET}")
            download_path = input(f"{Colors.LIGHT_CYAN}Enter the download path (leave empty for current directory): {Colors.RESET}")
            if not download_path:
                download_path = os.getcwd()
            action = input(f"{Colors.LIGHT_CYAN}Do you want to add this download to the queue or start immediately? (q/i): {Colors.RESET}")
            if action == 'i':
                download_video(url, 'bestvideo+bestaudio/best', download_path)
            else:
                add_download_to_queue(url, 'bestvideo+bestaudio/best', download_path, config)
                print_colored("Added to download queue.", Colors.LIGHT_GREEN)
        elif choice == '4':
            playlist_url = input(f"{Colors.LIGHT_CYAN}Enter the playlist URL: {Colors.RESET}")
            download_path = input(f"{Colors.LIGHT_CYAN}Enter the download path (leave empty for current directory): {Colors.RESET}")
            if not download_path:
                download_path = os.getcwd()
            action = input(f"{Colors.LIGHT_CYAN}Do you want to add this playlist download to the queue or start immediately? (q/i): {Colors.RESET}")
            if action == 'i':
                download_playlist_best_audio(playlist_url, download_path)
            else:
                add_download_to_queue(playlist_url, 'bestaudio/best', download_path, config)
                print_colored("Added playlist download (Best Audio Quality) to the queue.", Colors.LIGHT_GREEN)
        elif choice == '5':
            playlist_url = input(f"{Colors.LIGHT_CYAN}Enter the playlist URL: {Colors.RESET}")
            download_path = input(f"{Colors.LIGHT_CYAN}Enter the download path (leave empty for current directory): {Colors.RESET}")
            if not download_path:
                download_path = os.getcwd()
            action = input(f"{Colors.LIGHT_CYAN}Do you want to add this playlist download to the queue or start immediately? (q/i): {Colors.RESET}")
            if action == 'i':
                download_playlist_best_quality(playlist_url, download_path)
            else:
                add_download_to_queue(playlist_url, 'bestvideo+bestaudio/best', download_path, config)
                print_colored("Added playlist download (Best Quality) to the queue.", Colors.LIGHT_GREEN)
        elif choice == '6':
            # Prompt user for next action
            print(f"{Colors.LIGHT_CYAN}Once the download queue has finished, what would you like to do next?{Colors.RESET}")
            print(f"{Colors.LIGHT_GREEN}1.{Colors.RESET} Keep system idle")
            print(f"{Colors.LIGHT_GREEN}2.{Colors.RESET} Shut down system after 60 seconds")
            print(f"{Colors.LIGHT_GREEN}3.{Colors.RESET} Sleep system after 60 seconds")

            post_queue_choice = input("Enter your choice: ")

            # Process the download queue
            process_queue(config)

            if post_queue_choice == '2':
                print_colored("System will shut down in 60 seconds.", Colors.LIGHT_CYAN)
                time.sleep(60)
                os.system("shutdown /s /t 0")
            elif post_queue_choice == '3':
                print_colored("System will sleep in 60 seconds.", Colors.LIGHT_CYAN)
                time.sleep(60)
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            else:
                print_colored("System will remain idle.", Colors.LIGHT_GREEN)
        elif choice == '7':
            update_and_restart_youtube()
        elif choice == '8':
            latest_version = get_latest_version_yt_dlp()
            local_version = get_local_version_yt_dlp()
            if latest_version and local_version != latest_version:
                print_colored(f"Downloading the latest version of yt-dlp (v{latest_version})...", Colors.LIGHT_CYAN)
                download_latest_version_yt_dlp(latest_version)
                print_colored("yt-dlp has been updated.", Colors.LIGHT_GREEN)
            else:
                print_colored("yt-dlp is already up-to-date.", Colors.LIGHT_GREEN)

        elif choice == '9':
            print_colored("Exiting the program. Goodbye!", Colors.LIGHT_CYAN)
            break
        else:
            print_colored("Invalid choice. Please try again.", Colors.LIGHT_RED)

if __name__ == "__main__":
    main()
