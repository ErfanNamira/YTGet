# 📥 YTGet
Welcome to YTGet! This is a simple and efficient script to manage and download YouTube videos using the yt-dlp executable. This tool offers features like internet connectivity checking, automatic updates for yt-dlp, downloading videos in specified formats, and managing a download queue.
## ✨ Features
* Automatically download the latest version of yt-dlp.
* Fetch and display available formats for YouTube videos.
* Add download tasks to a queue.
* Process and manage the download queue.
* Save and load configurations for persistent settings.
# 💻 Installation
1. Download the latest release from the releases page.
2. Extract the files to your desired location.
3. Run the script:
```
python YTGet.py
```
## 🚀 Usage
### Main Menu
When you run the script, you'll see the following menu:
```
1. Download A Single YouTube Address
2. Start Download Queue
3. Exit
```
### Download a Single YouTube Address
1. Choose option 1.
2. Enter the YouTube URL.
3. View available formats and enter the format code you want to download (e.g., 251 or 251+271).
4. Specify the download path or use the default path.
5. Choose whether to add the download to the queue or start immediately.
### Start Download Queue
1. Choose option 2.
The script will process all items in the queue and download them to the specified path.
### Configuration
The script uses a configuration file (YTGet_Conf.json) to store settings like the download path, queue, and failed downloads. The configuration is loaded at the start of the script and saved after every change.
## ⚙️ Configuration
The configuration is stored in a JSON file (YTGet_Conf.json). Here is an example of what the file might look like:
```
{
    "download_path": "/path/to/downloads",
    "queue": [],
    "failed_downloads": []
}
```
`*` download_path: The default path where downloads will be saved.
`*` queue: A list of download tasks waiting to be processed.
`*` failed_downloads: A list of downloads that failed.
## 📄 License
This project is licensed under the MIT License. See the LICENSE file for details.
