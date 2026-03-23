#!/usr/bin/env python3
"""
Add keyframes to a playlist to make it seamless.

Assumes each dream in the playlist follows exactly to the next.
Uses each dream's thumbnail as its start keyframe image, and sets
start/end keyframes so transitions are seamless:

  dream[0].start = kf[0]   dream[0].end = kf[1]
  dream[1].start = kf[1]   dream[1].end = kf[2]
  ...
  dream[N].start = kf[N]   dream[N].end = kf[0]  (if --loop)
"""

import sys
import os
import argparse
import tempfile
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client
from edream_sdk.types.dream_types import UpdateDreamRequest

load_dotenv()


def assure_keyframe(client, playlist, name, file_path=None):
    """Find an existing keyframe by name on the playlist, or create a new one."""
    for pk in playlist.get("playlistKeyframes", []):
        if pk["keyframe"].get("name") == name:
            return pk["keyframe"]
    keyframe = client.add_keyframe_to_playlist(playlist, name, file_path=file_path)
    return keyframe


def main():
    parser = argparse.ArgumentParser(
        prog="add_keyframes",
        description="Add keyframes to a playlist to make it seamless",
    )
    parser.add_argument(
        "playlist_uuid",
        nargs="?",
        default=os.getenv("PLAYLIST_UUID"),
        help="Playlist UUID (or set PLAYLIST_UUID env var)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing keyframes before adding new ones",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Connect last dream back to first for seamless looping",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    playlist_uuid = args.playlist_uuid
    if not playlist_uuid:
        print("ERROR: No playlist UUID provided. Pass as argument or set PLAYLIST_UUID env var.")
        sys.exit(1)

    api_key = os.getenv("API_KEY")
    if not api_key:
        print("ERROR: No API key found. Set API_KEY in your .env file.")
        sys.exit(1)

    backend_url = os.getenv("BACKEND_URL", "https://api-alpha.infinidream.ai/api/v1")
    client = create_edream_client(backend_url=backend_url, api_key=api_key)

    print(f"Fetching playlist {playlist_uuid}...")
    playlist = client.get_playlist(playlist_uuid)
    print(f"Playlist: {playlist.get('name', 'Unnamed')}")

    # Collect dreams in playlist order
    dreams = []
    for item in playlist.get("items", []):
        if item.get("type") == "dream" and item.get("dreamItem"):
            dreams.append(item["dreamItem"])

    if not dreams:
        print("No dreams found in playlist.")
        return

    print(f"Found {len(dreams)} dreams")

    # Optionally clear existing keyframes
    if args.clear and not args.dry_run:
        print("\nClearing existing keyframes...")
        for pk in playlist.get("playlistKeyframes", []):
            name = pk["keyframe"].get("name", "unnamed")
            print(f"  Deleting: {name}")
            client.delete_keyframe(pk["keyframe"]["uuid"])
        playlist = client.get_playlist(playlist_uuid)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a keyframe for each dream using its thumbnail
        print("\nDownloading thumbnails and creating keyframes...")
        keyframes = []

        for i, dream in enumerate(dreams):
            thumb_url = dream.get("thumbnail")
            dream_name = dream.get("name", f"dream_{i}")
            kf_name = f"kf_{dream_name}"

            if not thumb_url:
                print(f"  [{i}] {dream_name}: no thumbnail, skipping")
                keyframes.append(None)
                continue

            print(f"  [{i}] {dream_name}")

            if args.dry_run:
                keyframes.append({"name": kf_name, "uuid": "dry-run"})
                continue

            # Download the thumbnail
            thumb_path = os.path.join(tmpdir, f"thumb_{i}.jpg")
            try:
                client.download_file(thumb_url, thumb_path)
            except Exception as e:
                print(f"    Failed to download thumbnail: {e}")
                keyframes.append(None)
                continue

            keyframe = assure_keyframe(client, playlist, kf_name, file_path=thumb_path)
            keyframes.append(keyframe)
            print(f"    Keyframe: {keyframe.get('uuid')}")

        # Assign start/end keyframes to each dream
        print("\nAssigning keyframes to dreams...")
        for i, dream in enumerate(dreams):
            dream_name = dream.get("name", f"dream_{i}")
            start_kf = keyframes[i] if i < len(keyframes) else None

            # End keyframe = start keyframe of the next dream
            if i + 1 < len(dreams):
                end_kf = keyframes[i + 1] if (i + 1) < len(keyframes) else None
            elif args.loop and keyframes and keyframes[0]:
                end_kf = keyframes[0]
            else:
                end_kf = None

            start_uuid = start_kf["uuid"] if start_kf else None
            end_uuid = end_kf["uuid"] if end_kf else None

            # Skip if already correctly set
            cur_start = dream.get("startKeyframe")
            cur_end = dream.get("endKeyframe")
            if (
                cur_start
                and cur_start.get("uuid") == start_uuid
                and cur_end
                and cur_end.get("uuid") == end_uuid
            ):
                print(f"  [{i}] {dream_name}: already set, skipping")
                continue

            if args.dry_run:
                print(f"  [{i}] {dream_name}: would set start={start_uuid}, end={end_uuid}")
                continue

            update = {}
            if start_uuid:
                update["startKeyframe"] = start_uuid
            if end_uuid:
                update["endKeyframe"] = end_uuid

            if update:
                client.update_dream(dream["uuid"], UpdateDreamRequest(**update))
                print(f"  [{i}] {dream_name}: start={start_uuid}, end={end_uuid}")
            else:
                print(f"  [{i}] {dream_name}: no keyframes available")

    print("\nDone!")


if __name__ == "__main__":
    main()
