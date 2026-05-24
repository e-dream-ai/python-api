"""
Transfer all dreams and playlists from one user to another.

Source user: 8fe990d9-4a20-45ec-a56b-198dda7c4607
Target user: 0c7f91fc-084d-4003-91f3-ecc9b5f617b7
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from edream_sdk.client import create_edream_client

load_dotenv()

SOURCE_USER_UUID = "8fe990d9-4a20-45ec-a56b-198dda7c4607"
TARGET_USER_UUID = "0c7f91fc-084d-4003-91f3-ecc9b5f617b7"

TARGET_USER_ID = 133  # numeric ID for target user (Stream Dreamz)

api_key = os.getenv("API_KEY")
backend_url = os.getenv("BACKEND_URL", "https://api-alpha.infinidream.ai/api/v1")

client = create_edream_client(backend_url=backend_url, api_key=api_key)

# Fetch all dreams for the source user, paginating through all results
all_dreams = []
skip = 0
take = 48

while True:
    feed_data = client.feed.get_feed(
        take=take, skip=skip, user_uuid=SOURCE_USER_UUID, feed_type="dream"
    )
    dreams = feed_data.get("feed", [])
    if not dreams:
        break
    all_dreams.extend(dreams)
    total = feed_data.get("count", 0)
    skip += take
    if skip >= total:
        break

print(f"Found {len(all_dreams)} dreams for source user {SOURCE_USER_UUID}")

# Update each dream's owner to the target user
success = 0
failed = 0

for item in all_dreams:
    dream = item.get("dreamItem", {})
    if not dream:
        continue
    dream_uuid = dream["uuid"]
    dream_name = dream.get("name", "(unnamed)")
    try:
        client.update_dream(dream_uuid, {"user": TARGET_USER_UUID})
        success += 1
        print(f"  [{success}] Transferred: {dream_name} ({dream_uuid})")
    except Exception as e:
        failed += 1
        print(f"  FAILED: {dream_name} ({dream_uuid}) - {e}")

print(f"\nDreams done. Transferred: {success}, Failed: {failed}")

# Fetch all playlists for the source user, paginating through all results
all_playlists = []
skip = 0

while True:
    feed_data = client.feed.get_feed(
        take=take, skip=skip, user_uuid=SOURCE_USER_UUID, feed_type="playlist"
    )
    items = feed_data.get("feed", [])
    if not items:
        break
    all_playlists.extend(items)
    total = feed_data.get("count", 0)
    skip += take
    if skip >= total:
        break

print(f"\nFound {len(all_playlists)} playlists for source user {SOURCE_USER_UUID}")

# Update each playlist's owner to the target user
pl_success = 0
pl_failed = 0

for item in all_playlists:
    playlist = item.get("playlistItem", {})
    if not playlist:
        continue
    playlist_uuid = playlist["uuid"]
    playlist_name = playlist.get("name", "(unnamed)")
    try:
        client.update_playlist(playlist_uuid, {"name": playlist_name, "displayedOwner": TARGET_USER_ID})
        pl_success += 1
        print(f"  [{pl_success}] Transferred: {playlist_name} ({playlist_uuid})")
    except Exception as e:
        pl_failed += 1
        print(f"  FAILED: {playlist_name} ({playlist_uuid}) - {e}")

print(f"\nPlaylists done. Transferred: {pl_success}, Failed: {pl_failed}")
