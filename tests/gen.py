import os
import time
import json
import argparse
from dotenv import load_dotenv
from edream_sdk.client import create_edream_client

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "https://api-stage.infinidream.ai/api/v1")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://stage.infinidream.ai")

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
    "uprez": {
        "infinidream_algorithm": "uprez",
        "video_uuid": "d3f06c44-b453-4ea8-8985-fe0f97d607fe",
        "upscale_factor": 2,
        "interpolation_factor": 2,
        "output_format": "mp4",
        "tile_size": 1024,
        "tile_padding": 10,
        "quality": "high"
    },
    "qwen-image": {
        "infinidream_algorithm": "qwen-image",
        "prompt": "A fashion-forward woman sitting at cobblestone street in Paris, wearing a camel trench coat and high heels, wind catching her scarf, soft golden hour light hitting her cheekbones",
        "size": "1328*1328",
        "seed": -1,
        "negative_prompt": "",
        "enable_safety_checker": True
    },
    "wan-t2v": {
        "infinidream_algorithm": "wan-t2v",
        "prompt": "A serene morning in an ancient forest, golden sunlight filtering through tall pine trees, creating dancing light patterns on the moss-covered ground. Gentle mist drifts between the tree trunks as small particles float in the sunbeams. Camera slowly pans right revealing a small woodland stream with crystal clear water flowing over smooth stones.",
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
        "prompt": "an extremely cute animal in fantastical Joan Miró style. Children's book Illustration. White background. The animals are happy, they dance and wiggle with glee.",
        "image": "6adfec90-8803-4727-98ce-ec768be9a21d",
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
        "image": "6adfec90-8803-4727-98ce-ec768be9a21d",
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
    }
}

def poll_dream_status(client, dream_uuid: str, max_wait_seconds: int = 10800):
    print(f"\n{'='*60}")
    print(f"Polling dream status for: {dream_uuid}")
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
                print("Dream processing completed!")
                print(f"Video URL:          {dream.get('video', 'N/A')}")
                print(f"Thumbnail URL:      {dream.get('thumbnail', 'N/A')}")
                print(f"Original Video URL: {dream.get('original_video', 'N/A')}")
                print(f"\nView at: {FRONTEND_URL}/dream/{dream_uuid}\n")
                return True
            
            if current_status == "failed":
                print(f"\n{'='*60}")
                print("Dream processing failed!")
                print(f"{'='*60}\n")
                return False
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Error polling status: {e}")
            time.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"Timeout after {max_wait_seconds}s")
    print(f"{'='*60}\n")
    return False

def create_dream_from_prompt(algo: str, timeout: int = 10800):
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("ERROR: No API key found. Please check your .env file.")
        return
    
    if algo not in ALGORITHM_PROMPTS:
        print(f"ERROR: Unknown algorithm '{algo}'")
        print(f"Available algorithms: {', '.join(ALGORITHM_PROMPTS.keys())}")
        return
    
    edream_client = create_edream_client(
        backend_url=BACKEND_URL,
        api_key=api_key
    )
    
    prompt_data = ALGORITHM_PROMPTS[algo].copy()
        
    print(f"Creating dream with algorithm: {algo}")
    print(f"Prompt configuration:")
    print(json.dumps(prompt_data, indent=2))
    print()
    
    try:
        dream = edream_client.create_dream_from_prompt({
            "name": f"Test {algo} generation",
            "description": f"Generated using {algo} algorithm",
            "prompt": json.dumps(prompt_data),
        })
        
        dream_uuid = dream["uuid"]
        print(f"Dream created successfully!")
        print(f"Dream UUID: {dream_uuid}")
        print(f"Status: {dream.get('status', 'unknown')}")
        print()
        
        poll_dream_status(edream_client, dream_uuid, max_wait_seconds=timeout)
        
    except Exception as e:
        print(f"\nERROR: Failed to create dream: {e}\n")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(
        description="Generate dreams using AI algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available algorithms:
  {', '.join(ALGORITHM_PROMPTS.keys())}

Examples:
  python gen.py --algo animatediff
  python gen.py --algo uprez --timeout 7200
  python gen.py --algo qwen-image
  python gen.py --algo wan-t2v
  python gen.py --algo wan-i2v
  python gen.py --algo wan-i2v-lora
        """
    )
    
    parser.add_argument(
        "--algo",
        required=True,
        choices=list(ALGORITHM_PROMPTS.keys()),
        help="Algorithm to use for generation"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Maximum wait time in seconds for dream processing (default: 3600 = 1 hour)"
    )
    
    args = parser.parse_args()
    
    create_dream_from_prompt(args.algo, timeout=args.timeout)

if __name__ == "__main__":
    main()

