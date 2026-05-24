#!/usr/bin/env python3
"""
Add keyframes to each dream in a playlist using filmstrip frames.

For each dream, the first and last frames from its filmstrip are treated
as endpoints. Endpoints across all dreams are clustered by perceptual
similarity (approximate match, not pixel-exact). Each cluster becomes a
single shared keyframe, so when dream A's last frame matches dream B's
first frame they reuse the same keyframe -- producing seamless chains.

Requires: Pillow, imagehash
"""

import sys
import os
import re
import argparse
import tempfile
from dotenv import load_dotenv

from PIL import Image
import imagehash

from edream_sdk.client import create_edream_client
from edream_sdk.types.dream_types import UpdateDreamRequest

load_dotenv()


# Matches "<id> → <id>" or "<id> -> <id>" inside a dream name; the IDs may be
# hex UUIDs or any non-whitespace token (we just need them to compare equal).
NAME_ARROW_RE = re.compile(r"(\S+)\s*(?:→|->)\s*(\S+)")


def phash(path):
    with Image.open(path) as img:
        return imagehash.phash(img.convert("RGB"))


def assure_keyframe(client, playlist, name, file_path):
    """Reuse an existing playlist keyframe by name, else upload a new one."""
    for pk in playlist.get("playlistKeyframes", []):
        if pk["keyframe"].get("name") == name:
            return pk["keyframe"]
    return client.add_keyframe_to_playlist(playlist, name, file_path=file_path)


def cluster_by_image(endpoints, threshold):
    """Greedy single-link cluster endpoints by perceptual-hash distance.
    Returns list of (name, [endpoints]) with auto-generated names."""
    clusters = []
    for ep in endpoints:
        if ep is None:
            continue
        joined = False
        for cluster in clusters:
            if any((ep["hash"] - m["hash"]) <= threshold for m in cluster):
                cluster.append(ep)
                joined = True
                break
        if not joined:
            clusters.append([ep])
    return [(f"kf_strip_{i}", c) for i, c in enumerate(clusters)]


def cluster_by_name(endpoints, dreams):
    """Cluster endpoints by parsing each dream's name as '<start> → <end>'.
    The parsed token becomes the cluster's keyframe name. Endpoints whose
    name can't be parsed become singleton clusters with auto-generated names.
    Returns list of (name, [endpoints])."""
    by_token = {}
    singletons = []
    for ep in endpoints:
        if ep is None:
            continue
        name = dreams[ep["dream_idx"]].get("name", "") or ""
        m = NAME_ARROW_RE.search(name)
        if not m:
            singletons.append(ep)
            continue
        token = m.group(1) if ep["role"] == "start" else m.group(2)
        by_token.setdefault(token, []).append(ep)
    named = list(by_token.items())
    named.extend(
        (f"kf_strip_unmatched_{i}", [ep]) for i, ep in enumerate(singletons)
    )
    return named


def main():
    parser = argparse.ArgumentParser(
        prog="add_keyframes_from_filmstrip",
        description="Add keyframes to dreams using filmstrip endpoint matching",
    )
    parser.add_argument("playlist_uuid", help="Playlist UUID")
    parser.add_argument(
        "--cluster",
        choices=("image", "name"),
        default="image",
        help="How to group endpoints into shared keyframes: 'image' compares filmstrip pHashes; 'name' parses each dream name as '<start> -> <end>' (default: image)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=8,
        help="Max perceptual-hash distance for image clustering (default 8; 0=identical, ~64=opposite). Ignored when --cluster name.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete existing playlist keyframes before adding new ones",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    api_key = os.getenv("API_KEY")
    if not api_key:
        print("ERROR: No API key found. Set API_KEY in your .env file.")
        sys.exit(1)

    backend_url = os.getenv("BACKEND_URL", "https://api-alpha.infinidream.ai/api/v1")
    client = create_edream_client(backend_url=backend_url, api_key=api_key)

    print(f"Fetching playlist {args.playlist_uuid}...")
    playlist = client.get_playlist(args.playlist_uuid)
    print(f"Playlist: {playlist.get('name', 'Unnamed')}")

    dreams = [
        item["dreamItem"]
        for item in playlist.get("items", [])
        if item.get("type") == "dream" and item.get("dreamItem")
    ]

    if not dreams:
        print("No dreams found in playlist.")
        return

    print(f"Found {len(dreams)} dreams")

    if args.clear and not args.dry_run:
        print("\nClearing existing playlist keyframes...")
        for pk in playlist.get("playlistKeyframes", []):
            name = pk["keyframe"].get("name", "unnamed")
            print(f"  Deleting: {name}")
            client.delete_keyframe(pk["keyframe"]["uuid"])
        playlist = client.get_playlist(args.playlist_uuid)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Download first and last filmstrip frame per dream, compute pHashes.
        # endpoints[i] = {"dream_idx", "role" ("start"|"end"), "hash", "path"}
        print("\nDownloading filmstrip endpoints...")
        endpoints = []
        for i, dream in enumerate(dreams):
            name = dream.get("name", f"dream_{i}")
            # Dream object from list endpoint may not include filmstrip; refetch.
            full = client.get_dream(dream["uuid"]) or dream
            dreams[i] = full
            strip = full.get("filmstrip") or []
            if len(strip) < 2:
                print(f"  [{i}] {name}: filmstrip has {len(strip)} frames, skipping")
                endpoints.append(None)
                endpoints.append(None)
                continue

            # Filmstrip entries are dicts {frameNumber, url}; sort by frameNumber.
            ordered = sorted(strip, key=lambda f: f.get("frameNumber", 0))
            first_url = ordered[0]["url"]
            last_url = ordered[-1]["url"]
            first_path = os.path.join(tmpdir, f"d{i}_first.jpg")
            last_path = os.path.join(tmpdir, f"d{i}_last.jpg")
            if not (client.download_file(first_url, first_path)
                    and client.download_file(last_url, last_path)):
                print(f"  [{i}] {name}: filmstrip download failed")
                endpoints.append(None)
                endpoints.append(None)
                continue

            endpoints.append({
                "dream_idx": i, "role": "start",
                "hash": phash(first_path), "path": first_path,
            })
            endpoints.append({
                "dream_idx": i, "role": "end",
                "hash": phash(last_path), "path": last_path,
            })
            print(f"  [{i}] {name}: ok")

        if args.cluster == "image":
            clusters = cluster_by_image(endpoints, args.threshold)
        else:
            clusters = cluster_by_name(endpoints, dreams)

        # Report clustering
        print(f"\nClustered {sum(1 for e in endpoints if e)} endpoints into {len(clusters)} keyframes (mode={args.cluster}):")
        for kf_name, cluster in clusters:
            members = ", ".join(
                f"d{ep['dream_idx']}.{ep['role']}" for ep in cluster
            )
            shared = "SHARED" if len(cluster) > 1 else "unique"
            print(f"  {kf_name}: {shared} ({members})")

        # Create (or reuse) one keyframe per cluster.
        print("\nCreating keyframes...")
        kf_for = {}  # (dream_idx, role) -> keyframe
        for kf_name, cluster in clusters:
            if args.dry_run:
                keyframe = {"uuid": "dry-run", "name": kf_name}
                print(f"  would create {kf_name}")
            else:
                # Use the first endpoint image of the cluster as the keyframe image.
                keyframe = assure_keyframe(client, playlist, kf_name, file_path=cluster[0]["path"])
                print(f"  {kf_name}: {keyframe.get('uuid')}")
            for ep in cluster:
                kf_for[(ep["dream_idx"], ep["role"])] = keyframe

        # Assign start/end keyframes on each dream.
        print("\nAssigning keyframes to dreams...")
        for i, dream in enumerate(dreams):
            name = dream.get("name", f"dream_{i}")
            start_kf = kf_for.get((i, "start"))
            end_kf = kf_for.get((i, "end"))

            start_uuid = start_kf["uuid"] if start_kf else None
            end_uuid = end_kf["uuid"] if end_kf else None

            if not start_uuid and not end_uuid:
                print(f"  [{i}] {name}: no endpoints, skipping")
                continue

            cur_start = dream.get("startKeyframe")
            cur_end = dream.get("endKeyframe")
            if (
                cur_start and cur_start.get("uuid") == start_uuid
                and cur_end and cur_end.get("uuid") == end_uuid
            ):
                print(f"  [{i}] {name}: already set, skipping")
                continue

            if args.dry_run:
                print(f"  [{i}] {name}: would set start={start_uuid}, end={end_uuid}")
                continue

            update = {}
            if start_uuid:
                update["startKeyframe"] = start_uuid
            if end_uuid:
                update["endKeyframe"] = end_uuid
            client.update_dream(dream["uuid"], UpdateDreamRequest(**update))
            print(f"  [{i}] {name}: start={start_uuid}, end={end_uuid}")

    print("\nDone!")


if __name__ == "__main__":
    main()
