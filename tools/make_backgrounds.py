"""Make the AI photo backgrounds once and save them in backgrounds/.

Uses Pollinations (free, no API key). Run from GitHub Actions with the
"Make AI backgrounds" workflow, or locally: python tools/make_backgrounds.py
Existing files are kept, so re-running only fills in what is missing.
Delete a file to make a new version of it.
"""
import os
import sys
import time
import urllib.parse

import requests

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backgrounds")

STYLE = (
    "cinematic editorial photograph, dark moody lighting, deep navy blue and warm gold tones, "
    "shallow depth of field, lots of empty dark space in the upper half, premium luxury finance magazine look, "
    "no text, no letters, no words, no logos, no watermark"
)

PROMPTS = {
    "compounding_1": "a small green sapling growing out of a neat stack of gold coins on a dark wooden desk, India",
    "compounding_2": "rising stacks of gold coins of increasing height arranged left to right, soft spotlight",
    "compounding_3": "a hand placing one gold coin on top of a tall stack at golden hour, close-up",
    "emergency_1": "a sturdy closed umbrella resting against a vintage safe in a dim elegant room",
    "emergency_2": "an open glass jar filled with Indian rupee notes and coins on a kitchen counter, warm light",
    "emergency_3": "a calm Indian family silhouette looking out of a window at evening city lights",
    "budget_1": "a leather notebook, a brass pen and a calculator on a dark desk, top-down view",
    "budget_2": "three neat piles of Indian rupee notes of different heights on a dark marble table",
    "budget_3": "a young Indian professional reviewing a phone banking app at a cafe table, evening, blurred background",
}


def fetch(name, prompt, seed):
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(f"{prompt}, {STYLE}")
    params = {"width": 1080, "height": 1350, "seed": seed, "nologo": "true", "model": "flux"}
    for attempt in range(5):
        try:
            res = requests.get(url, params=params, timeout=180)
            if res.ok and res.headers.get("content-type", "").startswith("image/"):
                return res.content
            print(f"{name}: HTTP {res.status_code}, retrying")
        except requests.RequestException as err:
            print(f"{name}: {err}, retrying")
        time.sleep(15 * (attempt + 1))
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    failed = []
    for seed, (name, prompt) in enumerate(PROMPTS.items(), start=101):
        path = os.path.join(OUT, f"{name}.jpg")
        if os.path.exists(path):
            print(f"{name}: already exists, skipping")
            continue
        data = fetch(name, prompt, seed)
        if not data:
            failed.append(name)
            continue
        # Save as JPEG whatever format came back
        from io import BytesIO
        from PIL import Image
        Image.open(BytesIO(data)).convert("RGB").save(path, "JPEG", quality=90)
        print(f"{name}: saved")
        time.sleep(5)  # stay inside the free rate limit
    if failed:
        print("Failed:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
