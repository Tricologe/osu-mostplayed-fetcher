# osu! Most Played Fetcher

We all "quit" osu! at some point and delete our maps, only to come back crawling and regretting it. I made this script out of pure laziness so I could just fetch my most played maps automatically instead of clicking the download button 100 times on the website.

[![Download for Windows](https://img.shields.io/badge/Download-For_Windows-0078D6?style=for-the-badge&logo=windows)](https://github.com/Tricologe/osu-mostplayed-fetcher/releases/download/v1.0.0/osumostplayedfetcher.exe)

## Features
- **Smart Resume:** Skips fully downloaded maps and automatically redownloads corrupted/incomplete ones.
- **Dynamic Folders:** Creates and saves maps directly into a `[Username]'s Most Played Beatmaps` directory.
- **API Safe:** Built-in delays and retry mechanisms to prevent rate-limiting.

## Usage

### Method 1: Standalone Executable (Recommended)
1. Download `osumostplayedfetcher.exe` from the **Releases** tab.
2. Place it in any folder and run the program.
3. Enter your osu! User ID and set the download limit.

### Method 2: Running the Python Script
Ensure Python is installed on your system.
1. Clone this repository or download the source code.
2. Install the required dependencies:
   `python -m pip install requests`
3. Run the script via terminal or command prompt:
   `python osumostplayedfetcher.py`

### Importing Beatmaps

**For osu! (Stable):**
- **Method 1:** Select the downloaded `.osz` files and drag-and-drop them directly into the open game window.
- **Method 2:** Move all the `.osz` files into your `osu!\Songs` directory, open the beatmap selection menu in-game, and press `F5` to refresh your database.

**For osu!lazer:**
- **Method 1:** Drag and drop the `.osz` files into the open osu!lazer window.
- **Method 2:** Open osu!lazer settings, search for "Import", click "Import files from a folder", and select the folder where the script saved your downloaded maps.

## Build from Source
If you want to compile the Python script into a standalone `.exe` file yourself:

1. Clone the repository and install dependencies:
   `python -m pip install requests pyinstaller`
2. Compile the script:
   `python -m PyInstaller --onefile osumostplayedfetcher.py`
3. The compiled `.exe` will be generated inside the `dist` folder.

## License
MIT License. See the LICENSE file for details.