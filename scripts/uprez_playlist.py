"""Create a derived uprez playlist from a source playlist, using the
backend's native `uprez_playlist` algorithm.

The backend supports a *derived* playlist: one whose own `prompt` names a
source playlist and the per-dream algorithm to apply. Creating the derived
dreams is then the backend's job, not ours -- `POST /playlist/{uuid}/run`
reconciles the derived playlist against its source.

    {
      "infinidream_algorithm": "uprez_playlist",
      "source_playlist_uuid": "<source>",
      "dream_algorithm": "uprez",
      "params": { "upscale_factor": 2, "interpolation_factor": 2, ... }
    }

Do NOT hand-build the derived dreams (which is what
engines/scripts/run_uprez_batch.py does, and what an earlier version of this
script did). The backend links each derived dream to its origin by writing
`source_dream_uuid` into the dream's prompt, and everything good depends on
that link:

  * re-running only creates what is missing (created / kept / removed / skipped)
  * derived dreams left in `failed` are automatically requeued
  * `POST /playlist/{uuid}/cancel` can stop the whole playlist at once -- it
    skips any dream without `source_dream_uuid`
  * playlist keyframes are built and wired across the playlist, with loop
    detection, so it plays continuously

Hand-built dreams have no such link: they are invisible to the reconciler,
which would leave them as strays *and* create a duplicate set beside them.

`/run` and `/cancel` require the CREATOR or ADMIN role.

    python scripts/uprez_playlist.py <source_uuid> [<source_uuid> ...] --dry-run
    python scripts/uprez_playlist.py b3b3ab87-... d2167537-...
    python scripts/uprez_playlist.py --cancel <derived_uuid>
"""

import os
import sys
import json
import argparse

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from edream_sdk.client import create_edream_client


def build_playlist_prompt(source_uuid, args):
    """The playlist-level prompt. `params` is spread verbatim onto every
    derived dream, so anything the container should not default must be
    named here -- notably tile_size, which the container defaults to 512."""
    return {
        "infinidream_algorithm": "uprez_playlist",
        "source_playlist_uuid": source_uuid,
        "dream_algorithm": "uprez",
        "params": {
            "upscale_factor": args.upscale_factor,
            "interpolation_factor": args.interpolation_factor,
            "output_format": args.output_format,
            "tile_size": args.tile_size,
            "tile_padding": args.tile_padding,
            "quality": args.quality,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("playlists", nargs="+",
                        help="Source playlist UUID(s), or derived UUID(s) with --cancel")
    parser.add_argument("--upscale-factor", type=int, default=2)
    parser.add_argument("--interpolation-factor", type=int, default=2)
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    parser.add_argument("--output-format", default="mp4")
    parser.add_argument("--tile-size", type=int, default=1024,
                        choices=[256, 512, 1024, 2048])
    parser.add_argument("--tile-padding", type=int, default=10)
    parser.add_argument("--suffix", default="uprez",
                        help="Appended to the source playlist name (default: 'uprez')")
    parser.add_argument("--run", dest="run", action="store_true", default=True,
                        help="Run immediately after creating (default)")
    parser.add_argument("--no-run", dest="run", action="store_false",
                        help="Create the derived playlist but do not enqueue yet")
    parser.add_argument("--cancel", action="store_true",
                        help="Cancel in-flight jobs for the given DERIVED playlist(s)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    frontend_url = os.environ["FRONTEND_URL"]
    client = create_edream_client(backend_url=os.environ["BACKEND_URL"],
                                  api_key=os.environ["API_KEY"])

    if args.cancel:
        for uuid in args.playlists:
            pl = client.get_playlist(uuid)
            if args.dry_run:
                print(f"would cancel {pl['name']} ({uuid})")
                continue
            r = client.api_client.post(f"/playlist/{uuid}/cancel", {})
            print(f"cancelled {pl['name']}: {json.dumps(r.get('data', r))}")
        return

    for source_uuid in args.playlists:
        source = client.get_playlist(source_uuid)
        eligible = sum(
            1 for i in source.get("items", [])
            if i.get("type") == "dream"
            and (i.get("dreamItem") or {}).get("status") == "processed"
        )
        total = len(source.get("items", []))
        prompt = build_playlist_prompt(source_uuid, args)
        name = f"{source['name']} ({args.suffix})"

        print(f"\n=== {source['name']} ({source_uuid}) ===")
        print(f"  {total} items, {eligible} processed and eligible")
        print(f"  new playlist: {name}")
        print(f"  prompt: {json.dumps(prompt)}")

        if args.dry_run:
            continue

        derived = client.create_playlist({
            "name": name,
            "description": (
                f"Uprez of \"{source['name']}\" ({source_uuid}) at "
                f"{args.upscale_factor}x resolution and "
                f"{args.interpolation_factor}x frame interpolation. "
                f"Derived playlist: re-run to sync with the source."),
            "prompt": prompt,
        })
        uuid = derived["uuid"]
        print(f"  created {uuid}  {frontend_url}/playlist/{uuid}")

        if not args.run:
            print("  --no-run: nothing enqueued yet")
            continue

        # The backend creates the derived dreams, links them to their sources,
        # orders them to match, enqueues them, and wires up keyframes.
        result = client.api_client.post(f"/playlist/{uuid}/run", {})
        summary = (result.get("data") or {}).get("result", result)
        print(f"  run: {json.dumps(summary)}")
        print(f"  {frontend_url}/playlist/{uuid}")


if __name__ == "__main__":
    main()
