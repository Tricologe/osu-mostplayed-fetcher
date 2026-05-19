import requests
import time
import os
import sys
import re
import random

# ==========================================
# PORTABLE PATH DETECTION
# ==========================================
# Determine if running as a compiled .exe or a standard .py script
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

FAILED_LOG_PATH = os.path.join(APPLICATION_PATH, 'failed_downloads.txt')
# ==========================================

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def clean_filename(filename):
    """Sanitize filenames to be safe for Windows/Mac/Linux folders."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def smart_request(url, is_stream=False):
    """Handles standard requests, rate limits (429), and connection drops."""
    headers = {"User-Agent": USER_AGENT}
    max_retries = 4
    base_wait = 5

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, stream=is_stream, allow_redirects=True, timeout=15)
            
            if response.status_code == 429:
                wait_time = int(response.headers.get("Retry-After", base_wait * (2 ** attempt)))
                print(f"\n   [!] Rate Limited. Waiting {wait_time}s before retrying...")
                time.sleep(wait_time)
                continue
            
            if response.status_code == 200:
                return response
                
            print(f"   [!] Server Error: {response.status_code}. Retrying...")
            time.sleep(3)
            
        except Exception as e:
            print(f"   [!] Connection Error: {e}. Retrying...")
            time.sleep(3)
            
    return None

def get_username(user_id: int) -> str:
    """Validates user ID and attempts to scrape the username from the profile page."""
    print("Validating User ID and fetching profile data...")
    response = requests.get(f"https://osu.ppy.sh/users/{user_id}", headers={"User-Agent": USER_AGENT})
    
    if response.status_code != 200:
        print(f"Error: User ID {user_id} not found.")
        input("Press Enter to exit...")
        exit()
        
    # Attempt to extract username from the HTML title (e.g., "<title>mrekk · player info | osu!</title>")
    match = re.search(r'<title>(.*?)\s*·', response.text)
    if match:
        username = match.group(1).strip()
        safe_username = clean_filename(username)
        print(f"User found: {safe_username}")
        return safe_username
    else:
        # Fallback just in case the osu! website layout changes
        print("User found!")
        return str(user_id)

def retrieve_most_played_beatmaps(user_id: int, limit: int, offset: int = 0, step: int = 100):
    """Fetches the user's most played beatmaps from the osu! API."""
    beatmaps = [] 
    print(f"\nFetching top {limit} maps...")

    while len(beatmaps) < limit:
        chunk_size = min(step, limit - len(beatmaps))
        url = f"https://osu.ppy.sh/users/{user_id}/beatmapsets/most_played?limit={chunk_size}&offset={offset}"
        
        response = smart_request(url)

        if not response:
            print("Failed to fetch data from osu! API after multiple attempts.")
            break

        data = response.json()
        if not data:
            print("No more maps found on this profile.")
            break
        
        beatmaps.extend(data)
        offset += len(data)
        print(f"   ...Found {len(beatmaps)} maps so far...")
        time.sleep(1) 

    return beatmaps

def download_beatmaps(beatmaps: list[dict], download_dir: str):
    """Processes downloads using the Nerinyan mirror with smart skipping."""
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print(f"\nCreated download directory at:\n-> {download_dir}\n")

    failed_downloads = []
    print("--- Starting Downloads ---")
    
    for i, beatmap in enumerate(beatmaps):
        beatmapset_id = beatmap["beatmap"]["beatmapset_id"] 
        raw_title = beatmap["beatmapset"]["title"]
        safe_title = clean_filename(raw_title)
        
        file_path = os.path.join(download_dir, f"{beatmapset_id} - {safe_title}.osz")
        prefix = f"[{i+1}/{len(beatmaps)}]"

        # Smart skip logic
        if os.path.exists(file_path):
            if os.path.getsize(file_path) > 20000:
                print(f"{prefix} Skipping: {raw_title} (Already exists)")
                continue
            else:
                print(f"{prefix} Corrupted file detected: {raw_title}. Redownloading...")
        else:
            print(f"{prefix} Downloading: {raw_title}")

        url = f"https://api.nerinyan.moe/d/{beatmapset_id}?noVideo=true"
        response = smart_request(url, is_stream=True)

        if response:
            try:
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print("   -> Success!")
            except Exception as e:
                print(f"   -> Failed to save file: {e}")
                failed_downloads.append(f"{beatmapset_id} - {raw_title}")
        else:
            print("   -> Download failed (Mirror might be busy).")
            failed_downloads.append(f"{beatmapset_id} - {raw_title}")
        
        # Random delay to prevent hammering the mirror
        time.sleep(random.uniform(1.5, 3.5))

    if failed_downloads:
        print(f"\nFinished with {len(failed_downloads)} errors. Saved list to {FAILED_LOG_PATH}")
        with open(FAILED_LOG_PATH, "w", encoding="utf-8") as f:
            for failed in failed_downloads:
                f.write(failed + "\n")
    else:
        print("\nAll maps downloaded successfully!")

if __name__ == "__main__":
    print("========================================")
    print("       OSU! MOST PLAYED FETCHER")
    print("========================================\n")

    try:
        user_id = int(input("Enter osu! User ID: ").strip())
    except ValueError:
        print("Invalid format. Numbers only (e.g., 1234567).")
        input("Press Enter to exit...")
        exit()
        
    # Fetch the username dynamically
    username = get_username(user_id)
    
    # Generate the custom folder name dynamically based on the username
    custom_folder_name = f"{username}'s Most Played Beatmaps"
    DYNAMIC_DOWNLOAD_DIR = os.path.join(APPLICATION_PATH, custom_folder_name)

    try:
        limit = int(input("How many maps to download? (e.g., 100): ").strip())
        offset = int(input("Offset (Enter 0 to start from the top): ").strip())
    except ValueError:
        print("Invalid input. Exiting.")
        input("Press Enter to exit...")
        exit()

    beatmaps = retrieve_most_played_beatmaps(user_id, limit, offset)
    
    if beatmaps:
        # Pass the dynamic directory to the download function
        download_beatmaps(beatmaps, DYNAMIC_DOWNLOAD_DIR)
    else:
        print("No beatmaps to download.")
    
    print("\n========================================")
    input("Process finished! Press Enter to exit...")