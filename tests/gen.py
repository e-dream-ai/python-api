import os
import time
import json
import argparse
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "https://api-stage.infinidream.ai/api/v1")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://stage.infinidream.ai")
DREAM_UUID = os.getenv("DREAM_UUID")  # video dream for endpoints that take video input
STILL_UUID = os.getenv("STILL_UUID")  # image dream for endpoints that take image input

ALGORITHM_PROMPTS = {
    "animatediff": {
        "infinidream_algorithm": "animatediff",
        "prompts": {
            "0": "a dog at park scene at afternoon",
            "32": "a dog running through the park",
            "48": "the dog chasing a ball",
            "64": "the dog returns happily"
        },
        "pre_text": "highly detailed, 4k, masterpiece",
        "app_text": "(Masterpiece, best quality:1.2) walking towards camera, full body closeup shot",
        "frame_count": 32,
        "frame_rate": 16,
        "width": 512,
        "height": 512,
        "steps": 12,
        "seed": 6
    },
    "deforum": {
        "infinidream_algorithm": "deforum",
        "0": "a fish on a bicycle",
        "width": 1024,
        "height": 576,
        "max_frames": 600,
        "fps": 16
    },
    "wan-t2v": {
        "infinidream_algorithm": "wan-t2v",
        "prompt": "A serene morning in an ancient forest, golden sunlight filtering through tall pine trees, creating dancing light patterns on the moss-covered ground.",
        "size": "1280*720",
        "duration": 5,
        "num_inference_steps": 30,
        "guidance": 5,
        "seed": -1,
        "negative_prompt": "",
        "flow_shift": 5,
        "enable_prompt_optimization": False,
        "enable_safety_checker": True
    },
    "wan-i2v": {
        "infinidream_algorithm": "wan-i2v",
        "prompt": "The scene comes alive with gentle motion.",
        "image": STILL_UUID,
        "size": "1280*720",
        "duration": 5,
        "num_inference_steps": 30,
        "guidance": 5,
        "seed": -1,
        "negative_prompt": "",
        "flow_shift": 5,
        "enable_prompt_optimization": False,
        "enable_safety_checker": False
    },
    "wan-i2v-lora": {
        "infinidream_algorithm": "wan-i2v-lora",
        "prompt": "orbit 180 around an astronaut on the moon.",
        "image": STILL_UUID,
        "duration": 5,
        "seed": -1,
        "high_noise_loras": [
            {
                "path": "https://huggingface.co/ostris/wan22_i2v_14b_orbit_shot_lora/resolve/main/wan22_14b_i2v_orbit_high_noise.safetensors",
                "scale": 1
            }
        ],
        "low_noise_loras": [
            {
                "path": "https://huggingface.co/ostris/wan22_i2v_14b_orbit_shot_lora/resolve/main/wan22_14b_i2v_orbit_low_noise.safetensors",
                "scale": 1
            }
        ],
        "enable_safety_checker": True
    },
    "ltx-i2v": {
        "infinidream_algorithm": "ltx-i2v",
        "prompt": "A cinematic shot of mountains.",
        "source_dream_uuid": STILL_UUID,
        "duration": 5,
        "seed": -1,
        "lora": "ltx-2-19b-lora-camera-control-static.safetensors",
        "lora_strength": 0.4
    },
    "qwen-image": {
        "infinidream_algorithm": "qwen-image",
        "prompt": "smiling cute furry creature drawn in fantastical and surreal children's book style. Colors are pastel. Black background.",
        "size": "1280*720",
        "seed": -1,
        "negative_prompt": "",
        "enable_safety_checker": True
    },
    "z-image-turbo": {
        "infinidream_algorithm": "z-image-turbo",
        "prompt": "A vibrant sunset over ocean waves, photorealistic.",
        "size": "1280*720",
        "seed": -1,
        "output_format": "png",
        "enable_safety_checker": True
    },
    "uprez": {
        "infinidream_algorithm": "uprez",
        "video_uuid": DREAM_UUID,
        "upscale_factor": 2,
        "interpolation_factor": 2,
        "output_format": "mp4",
        "tile_size": 1024,
        "tile_padding": 10,
        "quality": "high"
    },
    "nvidia-uprez": {
        "infinidream_algorithm": "nvidia-uprez",
        "video_uuid": DREAM_UUID,
        "upscale_factor": 2,
        "quality": "ULTRA"
    },
}


def poll_dream_status(client, dream_uuid: str, max_wait_seconds: int = 10800):
    print(f"\n{'='*60}")
    print(f"Polling: {dream_uuid}")
    print(f"{'='*60}\n")

    start_time = time.time()
    last_status = None

    while time.time() - start_time < max_wait_seconds:
        try:
            dream = client.get_dream(dream_uuid)
            current_status = dream.get("status", "unknown")

            if current_status != last_status:
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed}s] Status: {current_status}")
                last_status = current_status

            if current_status == "processed":
                print(f"Done. View at: {FRONTEND_URL}/dream/{dream_uuid}\n")
                return True

            if current_status == "failed":
                print(f"Failed: {dream.get('error', 'unknown error')}\n")
                return False

            time.sleep(5)

        except Exception as e:
            print(f"Error polling status: {e}")
            time.sleep(5)

    print(f"Timeout after {max_wait_seconds}s\n")
    return False


def run_algo(client, algo: str, timeout: int) -> bool:
    prompt_data = ALGORITHM_PROMPTS[algo].copy()

    if "image" in prompt_data and prompt_data["image"] is None:
        print(f"ERROR: {algo} requires STILL_UUID in .env")
        return False
    if "source_dream_uuid" in prompt_data and prompt_data["source_dream_uuid"] is None:
        print(f"ERROR: {algo} requires STILL_UUID in .env")
        return False
    if "video_uuid" in prompt_data and prompt_data["video_uuid"] is None:
        print(f"ERROR: {algo} requires DREAM_UUID in .env")
        return False

    print(f"\nAlgorithm: {algo}")
    print(json.dumps(prompt_data, indent=2))
    print()

    try:
        dream = client.create_dream_from_prompt({
            "name": f"Test {algo}",
            "description": f"Smoke test for {algo}",
            "prompt": json.dumps(prompt_data),
        })

        dream_uuid = dream["uuid"]
        print(f"Created: {dream_uuid} (status: {dream.get('status', 'unknown')})")

        return poll_dream_status(client, dream_uuid, max_wait_seconds=timeout)

    except Exception as e:
        print(f"ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Smoke test AI generation endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available algorithms: {', '.join(ALGORITHM_PROMPTS.keys())}"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--algo",
        choices=list(ALGORITHM_PROMPTS.keys()),
        help="Single algorithm to test"
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run one generation for every algorithm sequentially"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Max wait per job in seconds (default: 3600)"
    )

    args = parser.parse_args()

    api_key = os.getenv("API_KEY")
    if not api_key:
        print("ERROR: API_KEY not found in .env")
        return

    client = create_edream_client(backend_url=BACKEND_URL, api_key=api_key)

    algos = list(ALGORITHM_PROMPTS.keys()) if args.all else [args.algo]

    results = {}
    for algo in algos:
        results[algo] = run_algo(client, algo, args.timeout)

    if args.all:
        print("\n" + "="*60)
        print("Results:")
        for algo, ok in results.items():
            print(f"  {'OK' if ok else 'FAIL':4}  {algo}")
        print("="*60)


if __name__ == "__main__":
    main()
