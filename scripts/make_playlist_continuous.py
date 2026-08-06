#!/usr/bin/env python3
"""
Make a playlist perfectly continuous by generating transitions and keyframes.

Walks the playlist's playback sequence (recursing into nested playlists) and
finds every adjacent pair of dreams whose keyframes don't match, i.e. where
A.endKeyframe != B.startKeyframe. For each gap it:

  1. Ensures both boundary keyframes exist, creating them from the dream's
     filmstrip endpoints (first/last frame) when missing.
  2. Generates a transition video the same way Flow Studio does: a
     first+last-frame i2v dream (kling-25-i2v by default) whose start image is
     A's last frame and end image is B's first frame.
  3. Wires the transition's start/end keyframes to A's end and B's start.
  4. Inserts the transition into the playlist between A and B immediately —
     playback ignores unprocessed dreams, so the transition simply goes live
     the moment rendering finishes, even if this script is interrupted.

Re-running is a no-op: matched pairs are skipped, and existing transitions are
recognized by a TRANSITION:<a>:<b> stamp in their description. Transitions
whose rendering failed are removed from the playlist (at the end of the run,
or during the scan on a later run) so their gap is regenerated.
"""

import sys
import os
import json
import time
import argparse
import tempfile
from dotenv import load_dotenv

import requests

from edream_sdk.client import create_edream_client
from edream_sdk.types.dream_types import UpdateDreamRequest
from edream_sdk.types.playlist_types import PlaylistItemType

load_dotenv()

# Flow Studio's default "Abstract" preset transition prompt
# (frontend/src/components/pages/studio/constants/action-presets.ts).
DEFAULT_PROMPT = (
    "The scene transitions through a continuous, viscous metamorphosis, forms "
    "dissolving and rebuilding from within as though the material itself is "
    "alive. Shape bleeds into shape with cellular fluidity - no cut, no "
    "dissolve, no opacity ramp - only the slow-pressure pull of one state "
    "becoming another. Camera holds locked and still throughout. The "
    "transformation drives forward with organic inevitability, each "
    "intermediate state a coherent world briefly passing through."
)

MODEL_DURATIONS = {
    "kling-25-i2v": (5, 10),
    "kling-i2v": tuple(range(3, 16)),
    "ltx-i2v": (5, 10, 15, 20),
}


def stamp_for(a_uuid, b_uuid):
    return f"TRANSITION:{a_uuid}:{b_uuid}"


def walk_playlist(client, playlist_uuid, chain, entries, warnings):
    """Depth-first walk of a playlist, appending flattened dream entries.

    Each entry: {"dream", "chain"} where chain is the list of
    {"playlist": uuid, "item_id": id} containers from the top level down to
    the dream's direct container.
    """
    if any(c["playlist"] == playlist_uuid for c in chain):
        warnings.append(f"cycle detected at playlist {playlist_uuid}, not recursing")
        return
    probe = client.get_playlist_items(playlist_uuid, take=1)
    total = probe.get("totalCount", 0)
    if not total:
        return
    items = client.get_playlist_items(playlist_uuid, take=total).get("items", [])
    for item in sorted(items, key=lambda it: it.get("order", 0)):
        link = chain + [{"playlist": playlist_uuid, "item_id": item["id"]}]
        if item.get("type") == "dream" and item.get("dreamItem"):
            entries.append({"dream": item["dreamItem"], "chain": link})
        elif item.get("type") == "playlist" and item.get("playlistItem"):
            walk_playlist(client, item["playlistItem"]["uuid"], link, entries, warnings)


def placement(chain_a, chain_b):
    """Insertion point for a transition between two entries: the deepest
    common container playlist, right after A's item (or ancestor item) in it."""
    k = 0
    while (
        k < len(chain_a)
        and k < len(chain_b)
        and chain_a[k]["playlist"] == chain_b[k]["playlist"]
    ):
        k += 1
    return chain_a[k - 1]["playlist"], chain_a[k - 1]["item_id"]


def keyframes_match(a, b):
    a_end = a.get("endKeyframe") or {}
    b_start = b.get("startKeyframe") or {}
    return bool(a_end.get("uuid")) and a_end.get("uuid") == b_start.get("uuid")


def frame_url(dream, role):
    """URL of a dream's first ('start') or last ('end') frame.

    Prefers the keyframe image, then the filmstrip endpoint; image dreams use
    the image itself for both roles.
    """
    kf = dream.get("startKeyframe" if role == "start" else "endKeyframe") or {}
    if kf.get("image"):
        return kf["image"]
    if dream.get("mediaType") == "image":
        return dream.get("video") or dream.get("original_video") or dream.get("thumbnail")
    strip = [f for f in (dream.get("filmstrip") or []) if isinstance(f, dict) and f.get("url")]
    if len(strip) >= 2:
        ordered = sorted(strip, key=lambda f: f.get("frameNumber", 0))
        return ordered[0]["url"] if role == "start" else ordered[-1]["url"]
    return None


def ensure_keyframe(client, dream, role, tmpdir, dry_run):
    """Make sure the dream has a start/end keyframe, creating one from its
    frame image if missing. Returns the keyframe uuid (or None on failure).
    Mutates the dream dict so later gaps see the new keyframe."""
    field = "startKeyframe" if role == "start" else "endKeyframe"
    existing = dream.get(field) or {}
    if existing.get("uuid"):
        return existing["uuid"]

    url = frame_url(dream, role)
    if not url:
        return None
    kf_name = f"kf_{dream['uuid'][:8]}_{role}"
    if dry_run:
        print(f"    would create keyframe {kf_name} for {dream.get('name')} ({role})")
        dream[field] = {"uuid": f"dry-run-{kf_name}", "image": url}
        return dream[field]["uuid"]

    path = os.path.join(tmpdir, f"{kf_name}.jpg")
    if not client.download_file(url, path):
        print(f"    ERROR: failed to download frame for {kf_name}")
        return None
    keyframe = client._create_keyframe(kf_name, file_path=path)
    client.update_dream(dream["uuid"], UpdateDreamRequest(**{field: keyframe["uuid"]}))
    dream[field] = keyframe
    print(f"    created keyframe {kf_name} = {keyframe['uuid']}")
    return keyframe["uuid"]


def build_prompt(model, prompt_text, negative_prompt, start_url, end_url, duration):
    p = {
        "infinidream_algorithm": model,
        "prompt": prompt_text,
        "source_dream_uuid": start_url,
        "end_source_uuid": end_url,
        "duration": duration,
    }
    if negative_prompt and negative_prompt.strip():
        p["negative_prompt"] = negative_prompt.strip()
    return p


def poll_dreams(client, uuids, timeout, interval=10):
    """Poll until every dream uuid is processed or failed. Returns
    {uuid: dream}."""
    pending = set(uuids)
    results = {}
    start = time.time()
    while pending and time.time() - start < timeout:
        for uuid in list(pending):
            dream = client.get_dream(uuid)
            status = (dream or {}).get("status")
            if status == "processed":
                print(f"  processed: {dream.get('name')}")
                results[uuid] = dream
                pending.discard(uuid)
            elif status == "failed":
                print(f"  FAILED: {dream.get('name')}: {dream.get('error')}")
                results[uuid] = dream
                pending.discard(uuid)
        if pending:
            elapsed = int(time.time() - start)
            print(f"  ... {len(pending)} still rendering ({elapsed}s)")
            time.sleep(interval)
    for uuid in pending:
        print(f"  TIMEOUT: {uuid} did not finish within {timeout}s")
        results[uuid] = client.get_dream(uuid)
    return results


def add_item_tolerating_duplicate(client, playlist_uuid, dream_uuid):
    """add-item, treating the backend's 409 (already in playlist) as success.
    Returns the playlist item id, or None if it must be looked up."""
    try:
        item = client.add_item_to_playlist(playlist_uuid, PlaylistItemType.DREAM, dream_uuid)
        return item["id"]
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 409:
            return None
        raise


def insert_transitions(client, container_uuid, insertions):
    """Insert transition dreams into a container playlist.

    insertions: ordered list of {"dream_uuid", "anchor_item_id"} — each
    transition goes immediately after its anchor item. Appends via add-item,
    then does a single full renumber. Returns {dream_uuid: playlist_item_id}.
    """
    item_ids = {}
    for ins in insertions:
        item_ids[ins["dream_uuid"]] = add_item_tolerating_duplicate(
            client, container_uuid, ins["dream_uuid"]
        )

    total = client.get_playlist_items(container_uuid, take=1).get("totalCount", 0)
    items = client.get_playlist_items(container_uuid, take=max(total, 1)).get("items", [])
    items.sort(key=lambda it: it.get("order", 0))

    # Resolve item ids for 409 cases, then split base items from transitions.
    for ins in insertions:
        if item_ids[ins["dream_uuid"]] is None:
            for it in items:
                if (it.get("dreamItem") or {}).get("uuid") == ins["dream_uuid"]:
                    item_ids[ins["dream_uuid"]] = it["id"]
                    break
    transition_item_ids = {v for v in item_ids.values() if v is not None}
    base = [it for it in items if it["id"] not in transition_item_ids]

    by_anchor = {}
    for ins in insertions:
        t_id = item_ids[ins["dream_uuid"]]
        if t_id is None:
            print(f"    WARNING: could not locate playlist item for {ins['dream_uuid']}")
            continue
        by_anchor.setdefault(ins["anchor_item_id"], []).append(t_id)

    final = []
    for it in base:
        final.append(it["id"])
        final.extend(by_anchor.pop(it["id"], []))
    for orphans in by_anchor.values():  # anchor item vanished; keep at end
        final.extend(orphans)

    client.reorder_playlist(container_uuid, [
        {"id": item_id, "order": i} for i, item_id in enumerate(final)
    ])

    check = client.get_playlist_items(container_uuid, take=max(len(final), 1)).get("items", [])
    check_ids = [it["id"] for it in sorted(check, key=lambda it: it.get("order", 0))]
    if check_ids != final:
        print(f"    WARNING: order verification mismatch in playlist {container_uuid}")
    return item_ids


def main():
    parser = argparse.ArgumentParser(
        prog="make_playlist_continuous",
        description="Generate transitions and keyframes so a playlist plays continuously",
    )
    parser.add_argument(
        "playlist_uuid",
        nargs="?",
        default=os.getenv("PLAYLIST_UUID"),
        help="Playlist UUID (or set PLAYLIST_UUID env var)",
    )
    parser.add_argument(
        "--model",
        choices=sorted(MODEL_DURATIONS),
        default="kling-25-i2v",
        help="Transition generation model (default: kling-25-i2v, same as Flow Studio)",
    )
    parser.add_argument(
        "--duration", type=int, default=5,
        help="Transition duration in seconds (default 5)",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT,
        help="Text prompt for transition generation (default: Flow Studio's Abstract preset)",
    )
    parser.add_argument("--negative-prompt", default=None, help="Optional negative prompt")
    parser.add_argument(
        "--loop", action="store_true",
        help="Also generate a wrap-around transition from the last dream back to the first",
    )
    parser.add_argument(
        "--recurse", action="store_true",
        help="Also fix gaps inside nested playlists (default: only modify the target playlist)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report gaps and planned actions without making changes",
    )
    parser.add_argument(
        "--timeout", type=int, default=3600,
        help="Max seconds to wait for generations (default 3600)",
    )
    args = parser.parse_args()

    if not args.playlist_uuid:
        print("ERROR: No playlist UUID provided. Pass as argument or set PLAYLIST_UUID env var.")
        sys.exit(1)
    if args.duration not in MODEL_DURATIONS[args.model]:
        print(f"ERROR: {args.model} supports durations {list(MODEL_DURATIONS[args.model])}, "
              f"got {args.duration}")
        sys.exit(1)

    api_key = os.getenv("API_KEY")
    if not api_key:
        print("ERROR: No API key found. Set API_KEY in your .env file.")
        sys.exit(1)
    backend_url = os.getenv("BACKEND_URL", "https://api-alpha.infinidream.ai/api/v1")
    client = create_edream_client(backend_url=backend_url, api_key=api_key)

    print(f"Fetching playlist {args.playlist_uuid}...")
    playlist = client.get_playlist(args.playlist_uuid, auto_populate=False)
    print(f"Playlist: {playlist.get('name', 'Unnamed')}")

    entries = []
    warnings = []
    walk_playlist(client, args.playlist_uuid, [], entries, warnings)
    for w in warnings:
        print(f"WARNING: {w}")
    # Drop transitions whose rendering failed in a previous run so their gap
    # is detected and regenerated below.
    kept = []
    for e in entries:
        dream = e["dream"]
        desc = dream.get("description") or ""
        if "TRANSITION:" in desc and dream.get("status") == "failed":
            container = e["chain"][-1]["playlist"]
            if container != args.playlist_uuid and not args.recurse:
                kept.append(e)
                continue
            if args.dry_run:
                print(f"  would remove failed transition: {dream.get('name')}")
            else:
                client.delete_item_from_playlist(container, e["chain"][-1]["item_id"])
                print(f"  removed failed transition: {dream.get('name')}")
            continue
        kept.append(e)
    entries = kept

    if len(entries) < 2:
        print(f"Only {len(entries)} dream(s) in playback sequence; nothing to do.")
        return
    print(f"Playback sequence: {len(entries)} dreams")

    # Existing transition stamps anywhere in the walked sequence.
    known_stamps = set()
    for e in entries:
        desc = e["dream"].get("description") or ""
        if "TRANSITION:" in desc:
            known_stamps.add(desc[desc.index("TRANSITION:"):].split()[0])

    # ---- Find gaps -------------------------------------------------------
    pairs = list(zip(entries, entries[1:]))
    if args.loop:
        pairs.append((entries[-1], entries[0]))

    gaps = []
    for idx, (ea, eb) in enumerate(pairs):
        a, b = ea["dream"], eb["dream"]
        label = f"{a.get('name', a['uuid'][:8])} → {b.get('name', b['uuid'][:8])}"
        is_loop_pair = args.loop and idx == len(pairs) - 1
        if a["uuid"] == b["uuid"]:
            continue
        if keyframes_match(a, b):
            print(f"  [ok]      {label}")
            continue
        if stamp_for(a["uuid"], b["uuid"]) in known_stamps:
            print(f"  [reused]  {label}: transition already exists")
            continue
        if a.get("status") != "processed" or b.get("status") != "processed":
            print(f"  [skip]    {label}: dream not processed")
            continue
        container, anchor_item_id = placement(
            ea["chain"], ea["chain"] if is_loop_pair else eb["chain"]
        )
        if is_loop_pair:
            # Wrap-around: always append at the end of the top-level playlist.
            container = args.playlist_uuid
            anchor_item_id = ea["chain"][0]["item_id"]
        if container != args.playlist_uuid and not args.recurse:
            print(f"  [skip]    {label}: inside nested playlist (use --recurse to fix)")
            continue
        print(f"  [gap]     {label}")
        gaps.append({
            "a": a, "b": b, "label": label,
            "container": container, "anchor_item_id": anchor_item_id,
        })

    if not gaps:
        print("\nNo gaps to fix. Playlist is continuous.")
        return
    print(f"\n{len(gaps)} gap(s) to fix")

    with tempfile.TemporaryDirectory() as tmpdir:
        # ---- Ensure boundary keyframes -----------------------------------
        print("\nEnsuring boundary keyframes...")
        for gap in gaps:
            gap["a_end_kf"] = ensure_keyframe(client, gap["a"], "end", tmpdir, args.dry_run)
            gap["b_start_kf"] = ensure_keyframe(client, gap["b"], "start", tmpdir, args.dry_run)

        # ---- Resolve frames + submit generations -------------------------
        print("\nSubmitting transition generations...")
        submitted = []
        for gap in gaps:
            start_url = frame_url(gap["a"], "end")
            end_url = frame_url(gap["b"], "start")
            if not start_url or not end_url or not gap["a_end_kf"] or not gap["b_start_kf"]:
                print(f"  [skip] {gap['label']}: missing frame or keyframe")
                continue
            prompt = build_prompt(
                args.model, args.prompt, args.negative_prompt,
                start_url, end_url, args.duration,
            )
            if args.dry_run:
                print(f"  would generate ({args.model}, {args.duration}s): {gap['label']}")
                continue
            dream = client.create_dream_from_prompt({
                "name": gap["label"],
                "description": f"Auto-generated transition {stamp_for(gap['a']['uuid'], gap['b']['uuid'])}",
                "prompt": json.dumps(prompt),
            })
            client.update_dream(dream["uuid"], UpdateDreamRequest(
                startKeyframe=gap["a_end_kf"], endKeyframe=gap["b_start_kf"],
            ))
            gap["transition_uuid"] = dream["uuid"]
            submitted.append(gap)
            print(f"  submitted: {gap['label']} ({dream['uuid']})")

        if args.dry_run:
            print("\nDry run complete. No changes made.")
            return
        if not submitted:
            print("\nNothing was submitted.")
            return

        # ---- Insert into playlists right away ----------------------------
        # Playback only serves processed dreams, so inserting before the
        # render completes is safe — and if this script is interrupted while
        # waiting, each transition still goes live on its own once processed.
        print("\nInserting transitions into playlist(s)...")
        by_container = {}
        for g in submitted:
            by_container.setdefault(g["container"], []).append({
                "dream_uuid": g["transition_uuid"],
                "anchor_item_id": g["anchor_item_id"],
            })
        item_ids = {}
        for container_uuid, insertions in by_container.items():
            print(f"  playlist {container_uuid}: inserting {len(insertions)} transition(s)")
            item_ids.update(insert_transitions(client, container_uuid, insertions))

        # ---- Poll --------------------------------------------------------
        print(f"\nWaiting for {len(submitted)} generation(s)...")
        results = poll_dreams(client, [g["transition_uuid"] for g in submitted], args.timeout)

        # ---- Remove failures so a re-run regenerates them ----------------
        failed = [
            g for g in submitted
            if (results.get(g["transition_uuid"]) or {}).get("status") == "failed"
        ]
        for g in failed:
            item_id = item_ids.get(g["transition_uuid"])
            if item_id is not None:
                client.delete_item_from_playlist(g["container"], item_id)
                print(f"  removed failed transition from playlist: {g['label']}")

    # ---- Report ----------------------------------------------------------
    print("\nSummary:")
    for g in submitted:
        dream = results.get(g["transition_uuid"]) or {}
        status = dream.get("status", "unknown")
        url = dream.get("frontendUrl", "")
        note = ""
        if status not in ("processed", "failed"):
            note = "  (still rendering; already in playlist, goes live when done)"
        print(f"  [{status}] {g['label']}  {url}{note}")
    if failed:
        print(f"\n{len(failed)} generation(s) failed and were removed; re-run to retry them.")

    # Final continuity check on the updated playlist.
    print("\nVerifying continuity...")
    entries2, warnings2 = [], []
    walk_playlist(client, args.playlist_uuid, [], entries2, warnings2)
    check_pairs = list(zip(entries2, entries2[1:]))
    if args.loop and entries2:
        check_pairs.append((entries2[-1], entries2[0]))
    broken = [
        f"{ea['dream'].get('name')} → {eb['dream'].get('name')}"
        for ea, eb in check_pairs
        if not keyframes_match(ea["dream"], eb["dream"])
    ]
    if broken:
        print(f"  {len(broken)} pair(s) still discontinuous:")
        for label in broken:
            print(f"    {label}")
    else:
        print("  Playlist is perfectly continuous!")


if __name__ == "__main__":
    main()
