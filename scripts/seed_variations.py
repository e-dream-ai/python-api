"""Create seed variations of every dream in a playlist, collected into a new
playlist.

For exploring what the model does with a fixed prompt: hold every generation
parameter constant and vary only `seed`, N times per source dream.

    python scripts/seed_variations.py <source_playlist_uuid> --count 4 --dry-run
    python scripts/seed_variations.py d2167537-... --count 4
    python scripts/seed_variations.py --dreams 04d7231c-...,35495743-... --count 4
    python scripts/seed_variations.py --dreams 04d7231c-... --count 0 --name "..."

Seeds are always written as concrete integers, never -1. This matters: -1 is
Deforum's "pick a random seed" sentinel and it does work, but the value it
picks is unrecoverable. The GPU container discards it (src/predict.py returns
only video_path; src/handler.py returns only the R2 URL), the worker writes
back nothing but the video path and render duration, and the dream's stored
prompt keeps the literal -1. A dream rendered with -1 can never be reproduced
or extended. Drawing the seed here instead puts it in the prompt, the dream
name, and the description.

Unlike uprez, there is no `seed_playlist` derived-playlist algorithm --
`uprez_playlist` is the only one the backend knows (backend
src/utils/playlist-prompt.util.ts), and its reconciler keys one derived dream
per source_dream_uuid, so it could not express N variations per source anyway.
Hand-building the dreams is therefore correct here, not a shortcut around the
reconciler. The tradeoff is that these dreams carry no source link, so
/playlist/{uuid}/run and /cancel do not apply to them.

--count 0 creates the playlist from the source dreams themselves without
rendering anything, which is how you retroactively collect variations you
already submitted.
"""

import os
import re
import sys
import json
import random
import argparse

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from edream_sdk.client import create_edream_client
from edream_sdk.types.playlist_types import PlaylistItemType

# Algorithms whose prompt carries no seed. Reseeding these is a no-op, so a
# source dream using one is skipped unless --force.
SEEDLESS_ALGORITHMS = {"uprez", "nvidia-uprez", "uprez_playlist"}

MAX_SEED = 2**31 - 1

# Reseeding an already-reseeded playlist would otherwise compound the suffix
# into "... reseed 1/4 (seed 123) reseed 1/2 (seed 456)".
RESEED_SUFFIX = re.compile(r"\s*reseed \d+/\d+ \(seed \d+\)\s*$")


def base_name(name):
    prev = None
    while name != prev:
        prev = name
        name = RESEED_SUFFIX.sub("", name)
    return name or "dream"


def parse_prompt(dream):
    raw = dream.get("prompt")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def source_dreams(client, args):
    """Return [(uuid, name, prompt_dict)] for the sources, in playlist order."""
    out = []
    if args.dreams:
        uuids = [u.strip() for u in ",".join(args.dreams).split(",") if u.strip()]
        for u in uuids:
            d = client.get_dream(u)
            out.append((d["uuid"], d.get("name") or u, parse_prompt(d)))
        return out

    playlist = client.get_playlist(args.playlist)
    print(f"source playlist: {playlist.get('name')} "
          f"({len(playlist.get('items') or [])} items)")
    for item in playlist.get("items") or []:
        if item.get("type") != "dream":
            continue
        d = item.get("dreamItem") or {}
        if not d.get("uuid"):
            continue
        # The playlist item's dreamItem is a summary and may omit `prompt`;
        # fetch the dream itself so we are reseeding the real parameters.
        full = client.get_dream(d["uuid"])
        out.append((full["uuid"], full.get("name") or full["uuid"], parse_prompt(full)))
    return out


def usable(name, prompt, force):
    if prompt is None:
        print(f"  SKIP {name}: prompt is absent or not JSON")
        return False
    algo = prompt.get("infinidream_algorithm")
    if algo in SEEDLESS_ALGORITHMS and not force:
        print(f"  SKIP {name}: {algo} takes no seed (--force to override)")
        return False
    if "seed" not in prompt and not force:
        print(f"  SKIP {name}: prompt has no seed field (--force to override)")
        return False
    return True


def main():
    ap = argparse.ArgumentParser(
        description="Create N seed variations of every dream in a playlist.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("playlist", nargs="?", help="source playlist uuid")
    src.add_argument("--dreams", action="append",
                     help="comma-separated dream uuids instead of a playlist")
    ap.add_argument("--count", type=int, default=4,
                    help="variations per source dream (default 4); "
                         "0 collects the sources themselves, rendering nothing")
    ap.add_argument("--name", help="name for the new playlist")
    ap.add_argument("--description", help="description for the new playlist")
    ap.add_argument("--into", help="add to this existing playlist instead of "
                                   "creating one")
    ap.add_argument("--seed", type=int, action="append",
                    help="use these exact seeds instead of drawing at random; "
                         "repeatable, must supply --count of them")
    ap.add_argument("--force", action="store_true",
                    help="reseed even sources with no seed field")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.count < 0:
        sys.exit("ERROR: --count must be >= 0")
    if args.seed and len(args.seed) != args.count:
        sys.exit(f"ERROR: got {len(args.seed)} --seed values but --count is "
                 f"{args.count}")

    load_dotenv()
    backend_url = os.environ.get("BACKEND_URL")
    api_key = os.environ.get("API_KEY")
    frontend_url = os.environ.get("FRONTEND_URL", "").rstrip("/")
    if not backend_url or not api_key:
        sys.exit("ERROR: BACKEND_URL and API_KEY must be set (.env)")

    client = create_edream_client(backend_url=backend_url, api_key=api_key)

    sources = source_dreams(client, args)
    if not sources:
        sys.exit("ERROR: no source dreams found")

    if args.count:
        sources = [s for s in sources if usable(s[1], s[2], args.force)]
        if not sources:
            sys.exit("ERROR: no source dream had a reseedable prompt")

    plan = []  # (label, source_uuid, seed, prompt_dict)
    for uuid, name, prompt in sources:
        if args.count == 0:
            plan.append((name, uuid, None, None))
            continue
        for i in range(1, args.count + 1):
            seed = (args.seed[i - 1] if args.seed
                    else random.randint(1, MAX_SEED))
            p = dict(prompt)
            p["seed"] = seed
            plan.append((f"{base_name(name)} reseed {i}/{args.count} "
                         f"(seed {seed})",
                         uuid, seed, p))

    verb = "collect" if args.count == 0 else "create"
    print(f"\nwould {verb} {len(plan)} dream(s) from {len(sources)} source(s)")
    for label, uuid, seed, _ in plan:
        print(f"  {label}" + (f"   [from {uuid[:8]}]" if seed is not None else ""))

    if args.dry_run:
        print("\n--dry-run: nothing created")
        return

    if args.into:
        playlist = client.get_playlist(args.into, auto_populate=False)
        print(f"\nadding to existing playlist: {playlist.get('name')}")
    else:
        default_name = (args.name
                        or (f"{base_name(sources[0][1])} - {args.count} "
                            f"seed variations"
                            if args.count else "seed variations"))
        desc = args.description or (
            f"Seed variations ({args.count} per source) of "
            f"{len(sources)} dream(s). Only `seed` differs from the source; "
            f"every other parameter is identical. Seeds are recorded in each "
            f"dream name and description."
            if args.count else
            f"{len(sources)} dream(s) collected as seed variations.")
        playlist = client.create_playlist({"name": default_name,
                                           "description": desc})
        print(f"\ncreated playlist: {playlist['uuid']}")

    created = 0
    for label, source_uuid, seed, prompt in plan:
        try:
            if prompt is None:
                item_uuid = source_uuid
            else:
                d = client.create_dream_from_prompt({
                    "name": label,
                    "description": (f"Seed variation of {source_uuid}. "
                                    f"Only seed changed: {seed}."),
                    "prompt": json.dumps(prompt),
                })
                item_uuid = d["uuid"]
            client.add_item_to_playlist(
                playlist_uuid=playlist["uuid"],
                type=PlaylistItemType.DREAM,
                item_uuid=item_uuid,
            )
            created += 1
            print(f"  ok  {item_uuid}  {label}")
        except Exception as e:
            print(f"  FAIL  {label}: {e}")

    print(f"\n{created}/{len(plan)} added")
    if frontend_url:
        print(f"{frontend_url}/playlist/{playlist['uuid']}")


if __name__ == "__main__":
    main()
