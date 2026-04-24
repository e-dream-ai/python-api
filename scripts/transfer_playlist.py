"""
Transfer ownership of a single playlist and all dreams in it to another user.

Usage:
    python scripts/transfer_playlist.py \
        --playlist <PLAYLIST_UUID> \
        --user <TARGET_USER_UUID>
"""

import argparse
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from edream_sdk.client import create_edream_client


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--playlist", required=True, help="Playlist UUID to transfer")
    parser.add_argument("--user", required=True, help="Target user UUID (new owner)")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("ERROR: API_KEY not found in environment (.env)")
        sys.exit(1)
    backend_url = os.getenv("BACKEND_URL", "https://api-alpha.infinidream.ai/api/v1")

    client = create_edream_client(backend_url=backend_url, api_key=api_key)

    print(f"Fetching playlist {args.playlist}...")
    playlist = client.get_playlist(args.playlist, auto_populate=True)
    playlist_name = playlist.get("name", "(unnamed)")
    items = playlist.get("items") or []
    dream_items = [it for it in items if it.get("type") == "dream" and it.get("dreamItem")]
    print(f"  '{playlist_name}' — {len(dream_items)} dreams")

    success = 0
    failed = 0
    for idx, item in enumerate(dream_items, 1):
        dream = item["dreamItem"]
        dream_uuid = dream["uuid"]
        dream_name = dream.get("name") or "(unnamed)"
        try:
            client.update_dream(dream_uuid, {"user": args.user})
            success += 1
            print(f"  [{idx}/{len(dream_items)}] Transferred: {dream_name} ({dream_uuid})")
        except Exception as e:
            failed += 1
            print(f"  [{idx}/{len(dream_items)}] FAILED: {dream_name} ({dream_uuid}) - {e}")

    print(f"\nDreams done. Transferred: {success}, Failed: {failed}")

    print(f"\nTransferring playlist ownership...")
    try:
        client.update_playlist(args.playlist, {"name": playlist_name, "user": args.user})
        after = client.get_playlist(args.playlist, auto_populate=False)
        owner = (after.get("user") or {}).get("uuid")
        if owner == args.user:
            print(f"  Playlist owner is now {owner}")
        else:
            print(f"  WARN: playlist owner is {owner!r} after update (expected {args.user}).")
            print(f"        Backend may not accept 'user' on playlist update.")
    except Exception as e:
        print(f"  FAILED to update playlist: {e}")


if __name__ == "__main__":
    main()
