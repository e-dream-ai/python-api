"""Render a two-LoRA blend ladder on alpha, as a new playlist.

Companion to gen_loras.py: that script renders each LoRA pure, this one
interpolates between a pair of them. Prompts, overrides and base parameters
are imported from gen_loras.py so there is one transcription of the developed
dreams, not two.

One LoRA is the "A" side and donates the prompt text and any parameter
overrides; the "B" side contributes only its trigger word and its share of the
weight. Weights always sum to 1.0, so each rung is a convex blend.

The default ladder is dyadic - 1/32, 1/16, 1/8, 1/4, 1/2 and their complements
3/4, 7/8, 15/16, 31/32 - nine rungs, dense at both ends where the perceptual
change per unit weight is fastest. (The first blend playlist used sixths:
1/24, 1/12, 1/6, 2/6, 3/6, 4/6, 5/6, 11/12, 23/24.)

Three modes, all writing a single playlist:

  --a/--b        one pair, swept across --ladder
  --pair A:B     several pairs (repeatable), each swept across --ladder and
                 grouped in the order given
  --all-pairs    every ordered pair at one fixed --weight - a contact sheet
                 rather than a ladder. Both directions of a pair are emitted
                 adjacently, since at 50/50 the only thing separating AB from
                 BA is which side donates the prompts (and its overrides).

    # dyadic ladder for one pair
    python tests/blend_loras.py --a kaleidoscope-style --b color-swirl-style --no-wait

    # 50/50 contact sheet of all 42 ordered pairs, short and legible
    python tests/blend_loras.py --all-pairs --frames 50 --first-prompt-only --no-wait

    # custom spectrum across several pairs
    python tests/blend_loras.py --ladder 0.1,0.25,0.5,0.75,0.9 \
        --pair ral-frctlgmtry:trichom-style \
        --pair ral-frctlgmtry:chrome-style --no-wait
"""

import os
import re
import sys
import json
import copy
import argparse
import itertools
from fractions import Fraction
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_loras import BASE, LORAS, ALIASES, poll_all   # noqa: E402

from edream_sdk.client import create_edream_client      # noqa: E402
from edream_sdk.types.playlist_types import PlaylistItemType  # noqa: E402
from edream_sdk.utils.env import require_env            # noqa: E402

load_dotenv()

BY_ALIAS = {l["alias"]: l for l in LORAS}

LORA_TAG = re.compile(r'<lora:[^>]*>\s*')

# B-side share of the weight, as exact rationals. A gets 1 - B.
LADDER = [Fraction(1, 32), Fraction(1, 16), Fraction(1, 8), Fraction(1, 4),
          Fraction(1, 2), Fraction(3, 4), Fraction(7, 8), Fraction(15, 16),
          Fraction(31, 32)]


def parse_ladder(spec: str):
    """'0.1,1/4,0.5' -> exact Fractions. Decimals stay exact: 0.1 -> 1/10."""
    out = []
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        f = Fraction(tok)
        if not 0 < f < 1:
            raise argparse.ArgumentTypeError(
                f"ladder step {tok} must be strictly between 0 and 1 "
                "(pure endpoints are the demo dreams, not blends)")
        out.append(f)
    if not out:
        raise argparse.ArgumentTypeError("empty ladder")
    return out


def parse_pair(spec: str):
    """'ral-frctlgmtry:trichom-style' -> (A, B) aliases."""
    if spec.count(":") != 1:
        raise argparse.ArgumentTypeError(f"--pair wants A:B, got {spec!r}")
    a, b = (t.strip() for t in spec.split(":"))
    for alias in (a, b):
        if alias not in ALIASES:
            raise argparse.ArgumentTypeError(f"unknown LoRA {alias!r}")
    if a == b:
        raise argparse.ArgumentTypeError(f"--pair sides must differ: {spec!r}")
    return a, b


def short(alias: str) -> str:
    """kaleidoscope-style -> kaleidoscope, ral-frctlgmtry -> frctlgmtry."""
    return alias.replace('-style', '').replace('ral-', '')


def blend_prompts(a: dict, b: dict, wa: float, wb: float, frames: int,
                  first_only: bool = False) -> dict:
    """A's prompt set, retagged with both LoRAs at wa/wb and both trigger words.

    Prompt keyframe times are compressed proportionally: the developed dreams
    run BASE['max_frames'] (2400) frames, so a 600-frame blend divides them by 4.

    At very short lengths that compression is counterproductive - 4 prompts
    across 50 frames gives each ~12 frames, too few for Deforum to settle on
    anything - so first_only keeps just the opening prompt and lets the whole
    clip evolve under it.
    """
    scale = frames / BASE["max_frames"]
    if first_only:
        opening = min(a["prompts"], key=int)
        items = [(opening, a["prompts"][opening])]
    else:
        items = list(a["prompts"].items())
    out = {}
    for key, text in items:
        body = LORA_TAG.sub('', text).strip()
        # Drop A's own trigger if the body already leads with it; we re-add both
        # below so all rungs are uniform. (Two of chrome-style's four prompts
        # omit it, so the source set is not self-consistent.)
        for trig in (a["trigger"], b["trigger"]):
            if body.startswith(trig + ','):
                body = body[len(trig) + 1:].strip()
        tags = f'<lora:{a["alias"]}:{wa:g}> <lora:{b["alias"]}:{wb:g}>'
        new_key = "0" if first_only else str(round(int(key) * scale))
        out[new_key] = f'{tags} {a["trigger"]}, {b["trigger"]}, {body}'
    return out


def build_prompt(a: dict, b: dict, wa: float, wb: float, frames: int,
                 strength: float, seed=None, first_only: bool = False) -> dict:
    p = copy.deepcopy(BASE)
    p.update(a["overrides"])          # A donates its parameter deviations too
    p["prompts"] = blend_prompts(a, b, wa, wb, frames, first_only)
    p["max_frames"] = frames
    p["strength_schedule"] = f"0:({strength:g})"
    if seed is not None:
        p["seed"] = seed
    return p


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--a", choices=ALIASES,
                        help="A side: donates prompts, overrides, and trigger")
    parser.add_argument("--b", choices=ALIASES,
                        help="B side: donates trigger word and weight only")
    parser.add_argument("--pair", type=parse_pair, action="append", metavar="A:B",
                        help="A ladder for this pair (repeatable); all pairs "
                             "land in one playlist, grouped in the order given")
    parser.add_argument("--ladder", type=parse_ladder, metavar="STEPS",
                        default=LADDER,
                        help="Comma-separated B-side shares, as decimals or "
                             "fractions, e.g. '0.1,0.25,0.5,0.75,0.9'. "
                             "Default: the dyadic 1/32..31/32 ladder")
    parser.add_argument("--all-pairs", action="store_true",
                        help="Every ordered pair of LoRAs, one dream each at "
                             "--weight, instead of a ladder")
    parser.add_argument("--weight", type=float, default=0.5,
                        help="B-side weight for --all-pairs (default: 0.5)")
    parser.add_argument("--first-prompt-only", action="store_true",
                        help="Use only the opening prompt; sensible below ~200 frames")
    parser.add_argument("--frames", type=int, default=600,
                        help="max_frames per dream (default: 600)")
    parser.add_argument("--strength", type=float, default=0.6,
                        help="strength_schedule as 0:(N) (default: 0.6)")
    parser.add_argument("--seed", type=int, default=None,
                        help=f"Override seed (default: {BASE['seed']})")
    parser.add_argument("--playlist", metavar="NAME",
                        help="Playlist name (default: derived from the run)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the plan and prompts, submit nothing")
    parser.add_argument("--no-wait", action="store_true",
                        help="Submit and exit without polling")
    parser.add_argument("--timeout", type=int, default=43200,
                        help="Max total poll wait in seconds (default: 12h)")
    args = parser.parse_args()

    jobs = []   # (label, a, b, wa, wb, description)

    if args.all_pairs:
        if args.a or args.b or args.pair:
            parser.error("--all-pairs covers every pair; drop --a/--b/--pair")
        wb = args.weight
        wa = 1 - wb
        # Both directions of each pair adjacent, so the only difference
        # between neighbours is which LoRA donated the prompts.
        for x, y in itertools.combinations(ALIASES, 2):
            for a_alias, b_alias in ((x, y), (y, x)):
                a, b = BY_ALIAS[a_alias], BY_ALIAS[b_alias]
                jobs.append((
                    f"{short(a_alias)}+{short(b_alias)}", a, b, wa, wb,
                    f"{wa:g}/{wb:g} blend of {a_alias} + {b_alias}. Prompts, "
                    f"trigger and overrides from {a_alias} ({a['src_uuid']}); "
                    f"{b_alias} contributes trigger and weight only. "
                    f"{args.frames} frames"
                    f"{', opening prompt only' if args.first_prompt_only else ''}."))
        default_name = f"LoRA pair matrix {wa:g}/{wb:g} ({args.frames} frames)"
    else:
        pairs = list(args.pair or [])
        if args.a or args.b:
            if not (args.a and args.b):
                parser.error("--a and --b must be given together")
            if args.a == args.b:
                parser.error("--a and --b must differ")
            pairs.insert(0, (args.a, args.b))
        if not pairs:
            parser.error("give --a/--b, --pair, or --all-pairs")

        compression = BASE["max_frames"] / args.frames
        for a_alias, b_alias in pairs:
            a, b = BY_ALIAS[a_alias], BY_ALIAS[b_alias]
            for f in args.ladder:
                wb = float(f)
                wa = 1 - wb
                jobs.append((
                    f"{short(a_alias)}+{short(b_alias)} "
                    f"{f.numerator}/{f.denominator}", a, b, wa, wb,
                    f"Blend ladder {f.numerator}/{f.denominator}: "
                    f"{a_alias} {wa:g} + {b_alias} {wb:g}, {args.frames} frames, "
                    f"prompt times compressed {compression:g}x from "
                    f"{a['src_uuid']}."))

        steps = "/".join(f"{float(f):g}" for f in args.ladder)
        if len(pairs) == 1:
            default_name = (f"{short(pairs[0][0])}/{short(pairs[0][1])} "
                            f"LoRA interpolation ({steps})")
        else:
            default_name = (f"LoRA spectrum interpolation - {len(pairs)} pairs "
                            f"x {len(args.ladder)} steps ({args.frames} frames)")

    if args.dry_run:
        for label, a, b, wa, wb, desc in jobs:
            print(f"--- {label}  ({a['alias']} {wa:g} + {b['alias']} {wb:g}) ---")
            print(json.dumps(build_prompt(a, b, wa, wb, args.frames, args.strength,
                                          args.seed, args.first_prompt_only),
                             indent=2))
        print(f"\n{len(jobs)} dream(s); playlist would be: "
              f"{args.playlist or default_name}")
        return

    backend_url = require_env("BACKEND_URL")
    frontend_url = require_env("FRONTEND_URL")
    client = create_edream_client(backend_url=backend_url,
                                  api_key=require_env("API_KEY"))

    if args.all_pairs:
        pl_desc = (
            f"Every ordered pair of the {len(ALIASES)} ral-* demo LoRAs blended "
            f"{1 - args.weight:g}/{args.weight:g}, {args.frames} frames each. "
            f"Both directions of each pair are adjacent: at equal weight the only "
            f"difference is which LoRA donates the prompts, trigger order and "
            f"overrides (the first named one). "
            f"strength_schedule 0:({args.strength:g}).")
    else:
        steps = ", ".join(f"{float(f):g}" for f in args.ladder)
        pl_desc = (
            f"Static two-LoRA blends across {len(pairs)} pair(s): "
            + "; ".join(f"{x} + {y}" for x, y in pairs) + ". "
            f"Each pair sweeps the B-side share through {steps}, grouped and in "
            f"ascending order. {args.frames} frames each, prompts and overrides "
            f"from the first-named LoRA with both trigger words, "
            f"strength_schedule 0:({args.strength:g}). Pure endpoints excluded.")

    pl = client.create_playlist({"name": args.playlist or default_name,
                                 "description": pl_desc})
    playlist_uuid = pl["uuid"]
    print(f"playlist {playlist_uuid}  {frontend_url}/playlist/{playlist_uuid}\n")

    submitted = []
    for label, a, b, wa, wb, desc in jobs:
        try:
            dream = client.create_dream_from_prompt({
                "name": label,
                "description": desc,
                "prompt": json.dumps(build_prompt(a, b, wa, wb, args.frames,
                                                  args.strength, args.seed,
                                                  args.first_prompt_only)),
            })
            uuid = dream["uuid"]
            submitted.append((label, uuid))
            print(f"submitted  {label:40}  {uuid}")
            # NB: this API rejects the plain string "dream" - it needs the enum.
            client.add_item_to_playlist(playlist_uuid, PlaylistItemType.DREAM, uuid)
        except Exception as e:
            print(f"SUBMIT FAILED  {label}: {e}")

    if not submitted:
        print("Nothing submitted.")
        return

    print(f"\n{len(submitted)} dream(s) queued.")
    print(f"playlist: {frontend_url}/playlist/{playlist_uuid}\n")

    if args.no_wait:
        for label, uuid in submitted:
            print(f"  {label:40}  {frontend_url}/dream/{uuid}")
        return

    poll_all(client, submitted, frontend_url, args.timeout)


if __name__ == "__main__":
    main()
