"""Render the Deforum LoRA demo set on alpha.

    python tests/gen_loras.py --list
    python tests/gen_loras.py --dry-run
    python tests/gen_loras.py                              # all 7, 2400 frames
    python tests/gen_loras.py --frames 50 --no-wait        # quick smoke test
    python tests/gen_loras.py --lora chrome-style --strength 0.5
    python tests/gen_loras.py --playlist "LoRA demos strength 0.5" --strength 0.5
"""

import os
import time
import json
import copy
import argparse
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client
from edream_sdk.types.playlist_types import PlaylistItemType
from edream_sdk.utils.env import require_env

load_dotenv()

# Settings shared by every dream in the developed set.
BASE = {
    'infinidream_algorithm': 'deforum',
    'width': 1344,
    'height': 768,
    'seed': 788322001,
    'steps': 25,
    'sampler_name': 'euler_ancestral',
    'scheduler': 'normal',
    'animation_prompts_negative': 'nsfw, nude',
    'animation_mode': '3D',
    'border': 'replicate',
    'angle': '0: (0)',
    'zoom': '0: 1.025',
    'animation_prompts_positive': '',
    'strength_schedule': '0:(0.6)',
    'max_frames': 2400,
}

# Per-LoRA prompts and deviations from BASE, as developed on the server.
LORAS = [
    {
        "alias": 'ral-frctlgmtry',
        "version_id": 303921,
        "trigger": 'ral-frctlgmtry',
        "src_uuid": '5b29fc35-acbe-4074-b408-9693f3902955',   # dream this was developed on
        "prompts": {
            '0': '<lora:ral-frctlgmtry:1> ral-frctlgmtry, pretty',
            '600': '<lora:ral-frctlgmtry:1> ral-frctlgmtry, happy',
            '1200': '<lora:ral-frctlgmtry:1> ral-frctlgmtry, mean',
            '1800': '<lora:ral-frctlgmtry:1> ral-frctlgmtry, funny',
        },
        "overrides": {},
    },
    {
        "alias": 'kaleidoscope-style',
        "version_id": 1019727,
        "trigger": 'ral-kldscop',
        "src_uuid": '4b8889c5-2a0b-42b2-a688-acdc276d1f1f',   # dream this was developed on
        "prompts": {
            '0': '<lora:kaleidoscope-style:1> ral-kldscop, wings and feathers, black background',
            '600': '<lora:kaleidoscope-style:1> ral-kldscop, hands contact juggling, black background',
            '1200': '<lora:kaleidoscope-style:1> ral-kldscop, seraphim dancing, black background',
            '1800': '<lora:kaleidoscope-style:1> ral-kldscop, merkaba unfolding, black background',
        },
        "overrides": {},
    },
    {
        "alias": 'trichom-style',
        "version_id": 275323,
        "trigger": 'ral-trichom',
        "src_uuid": '941230d3-f6a6-4f8f-8190-5867f3d56bab',   # dream this was developed on
        "prompts": {
            '0': '<lora:trichom-style:1> ral-trichom, mantis priest dialog',
            '600': '<lora:trichom-style:1> ral-trichom, mantis DJ dance party',
            '1200': '<lora:trichom-style:1> ral-trichom, mantis spider and insect nobility',
            '1800': '<lora:trichom-style:1> ral-trichom, mantis and harvestman swarm',
        },
        "overrides": {},
    },
    {
        "alias": 'color-swirl-style',
        "version_id": 284883,
        "trigger": 'ral-colorswirl',
        "src_uuid": 'b4333619-5712-482f-83e4-9d739621200b',   # dream this was developed on
        "prompts": {
            '0': '<lora:color-swirl-style:1> ral-colorswirl, fluffy clouds',
            '600': '<lora:color-swirl-style:1> ral-colorswirl, storm clouds',
            '1200': '<lora:color-swirl-style:1> ral-colorswirl, ocean waves shot through with lightning',
            '1800': '<lora:color-swirl-style:1> ral-colorswirl, crashing surf',
        },
        "overrides": {'zoom': '0: 1.03'},
    },
    {
        "alias": 'bismuth-style',
        "version_id": 255200,
        "trigger": 'ral-bismut',
        "src_uuid": '288cfe47-32e0-4887-923b-199aa9ec03de',   # dream this was developed on
        "prompts": {
            '0': '<lora:bismuth-style:1> ral-bismut, toy factory, a woman with minakari everywhere',
            '600': '<lora:bismuth-style:1> ral-bismut, shoe factory, a woman with arabic tattoos everywhere',
            '1200': '<lora:bismuth-style:1> ral-bismut, chip factory, a woman with japanese tattoos everywhere ',
            '1800': '<lora:bismuth-style:1> ral-bismut, chip factory, a woman with sparkles everywhere',
        },
        "overrides": {'animation_prompts_positive': 'black background'},
    },
    {
        "alias": 'chrome-style',
        "version_id": 233612,
        "trigger": 'ral-chrome',
        "src_uuid": 'a38d000b-9601-4a3b-a349-65babd868f47',   # dream this was developed on
        "prompts": {
            '0': '<lora:chrome-style:1> ral-chrome, androids made of ral-chrome, dance party in space, black background',
            '600': '<lora:chrome-style:1> ral-chrome, arachnids made of ral-chrome, dance party in space, black background',
            '1200': '<lora:chrome-style:1> cephalopods made of ral-chrome, dance party in space, black background',
            '1800': '<lora:chrome-style:1> nudibranchs made of ral-chrome, dance party in space, black background',
        },
        "overrides": {},
    },
    {
        "alias": 'holographic-style',
        "version_id": 595769,
        "trigger": 'ral-hlgrphic',
        "src_uuid": '3aab1722-7418-4a6a-b46c-12171c58e006',   # dream this was developed on
        "prompts": {
            '0': '<lora:holographic-style:1> spectrogram music visualization made of ral-hlgrphic',
            '600': '<lora:holographic-style:1> spectrogram music visualization made of ral-hlgrphic',
        },
        "overrides": {'animation_prompts_positive': 'black background'},
    },
]

ALIASES = [l["alias"] for l in LORAS]


def build_prompt(lora: dict, frames: int, strength: float, seed=None) -> dict:
    """BASE + this LoRA's developed prompts and overrides, with CLI overrides last."""
    p = copy.deepcopy(BASE)
    p.update(lora["overrides"])
    p["prompts"] = copy.deepcopy(lora["prompts"])
    p["max_frames"] = frames
    p["strength_schedule"] = f"0:({strength:g})"
    if seed is not None:
        p["seed"] = seed
    return p


def poll_all(client, jobs, frontend_url, max_wait_seconds):
    """Poll every submitted dream until each is processed or failed."""
    start = time.time()
    pending = {uuid: alias for alias, uuid in jobs}
    results = {}
    last = {}

    while pending and time.time() - start < max_wait_seconds:
        for uuid in list(pending):
            alias = pending[uuid]
            try:
                status = client.get_dream(uuid).get("status", "unknown")
            except Exception as e:
                print(f"  poll error ({alias}): {e}")
                continue

            if status != last.get(uuid):
                elapsed = int(time.time() - start)
                print(f"[{elapsed:5}s] {alias:26} {status}")
                last[uuid] = status

            if status in ("processed", "failed"):
                results[alias] = (status == "processed", uuid)
                del pending[uuid]

        if pending:
            time.sleep(10)

    for uuid, alias in pending.items():
        print(f"TIMEOUT {alias}")
        results[alias] = (False, uuid)

    print()
    print("=" * 72)
    for alias, _ in jobs:
        if alias in results:
            ok, uuid = results[alias]
            print(f"  {'OK' if ok else 'FAIL':4}  {alias:26}  {frontend_url}/dream/{uuid}")
    print("=" * 72)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lora", action="append", dest="loras", choices=ALIASES,
                        help="Run only this LoRA (repeatable). Default: all 7.")
    parser.add_argument("--frames", type=int, default=BASE["max_frames"],
                        help=f"max_frames (default: {BASE['max_frames']})")
    parser.add_argument("--strength", type=float, default=0.6,
                        help="strength_schedule as 0:(N) (default: 0.6)")
    parser.add_argument("--seed", type=int, default=None,
                        help=f"Override seed (default: {BASE['seed']})")
    parser.add_argument("--playlist", metavar="NAME",
                        help="Create a playlist with this name and add every dream to it")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts, submit nothing")
    parser.add_argument("--list", action="store_true", help="List LoRAs and trigger words")
    parser.add_argument("--no-wait", action="store_true", help="Submit and exit without polling")
    parser.add_argument("--timeout", type=int, default=43200,
                        help="Max total poll wait in seconds (default: 43200 = 12h)")
    args = parser.parse_args()

    if args.list:
        for l in LORAS:
            first = l["prompts"][min(l["prompts"], key=int)]
            print(f"{l['alias']:20} {l['trigger']:16} "
                  f"overrides={l['overrides'] or '-'}\n"
                  f"{'':20} {first[:96]}")
        return

    selected = [l for l in LORAS if not args.loras or l["alias"] in args.loras]

    if args.dry_run:
        for l in selected:
            print(f"--- {l['alias']} (from {l['src_uuid']}) ---")
            print(json.dumps(build_prompt(l, args.frames, args.strength, args.seed), indent=2))
        return

    backend_url = require_env("BACKEND_URL")
    frontend_url = require_env("FRONTEND_URL")
    api_key = require_env("API_KEY")
    client = create_edream_client(backend_url=backend_url, api_key=api_key)

    playlist_uuid = None
    if args.playlist:
        pl = client.create_playlist({
            "name": args.playlist,
            "description": f"ral-* LoRA set, strength_schedule 0:({args.strength:g}), "
                           f"{args.frames} frames",
        })
        playlist_uuid = pl["uuid"]
        print(f"playlist {playlist_uuid}  {frontend_url}/playlist/{playlist_uuid}\n")

    jobs = []
    for l in selected:
        prompt_data = build_prompt(l, args.frames, args.strength, args.seed)
        try:
            dream = client.create_dream_from_prompt({
                "name": f"{l['alias']} s{args.strength:g}",
                "description": f"{l['alias']} (trigger: {l['trigger']}), "
                               f"strength_schedule 0:({args.strength:g}), {args.frames} frames",
                "prompt": json.dumps(prompt_data),
            })
            uuid = dream["uuid"]
            jobs.append((l["alias"], uuid))
            print(f"submitted  {l['alias']:20}  {uuid}")
            if playlist_uuid:
                # NB: this API rejects the plain string "dream" - it needs the enum.
                client.add_item_to_playlist(playlist_uuid, PlaylistItemType.DREAM, uuid)
        except Exception as e:
            print(f"SUBMIT FAILED  {l['alias']}: {e}")

    if not jobs:
        print("Nothing submitted.")
        return

    print(f"\n{len(jobs)} dream(s) queued.")
    if playlist_uuid:
        print(f"playlist: {frontend_url}/playlist/{playlist_uuid}")
    print()

    if args.no_wait:
        for alias, uuid in jobs:
            print(f"  {alias:20}  {frontend_url}/dream/{uuid}")
        return

    poll_all(client, jobs, frontend_url, args.timeout)


if __name__ == "__main__":
    main()
