import os
import subprocess
import sys
import time
import requests
from generator import create_carousel_slides, todays_caption

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")
REPO_NAME = os.getenv("GITHUB_REPOSITORY") # e.g. "vsvivek1/TheIndianRupees"


def commit_and_get_urls(slides):
    # Configure git inside GitHub Actions runner
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"])
    
    # Add generated slides and commit them to main branch
    subprocess.run(["git", "add", "-A", "slides"])
    subprocess.run(["git", "commit", "-m", "Auto-generate daily carousel slides [skip ci]"])
    
    # Push back to repository
    push_res = subprocess.run(["git", "push"])
    if push_res.returncode != 0:
        print("Git push failed or nothing to commit.")
    
    # Use the commit SHA, not "main", so Instagram never gets a cached copy
    # of yesterday's slides from GitHub's CDN
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    public_urls = []
    for slide in slides:
        raw_url = f"https://raw.githubusercontent.com/{REPO_NAME}/{sha}/{slide}"
        public_urls.append(raw_url)
        print(f"Public Raw URL: {raw_url}")
        
    return public_urls

def wait_until_ready(container_id, timeout=300, interval=10):
    """Instagram processes media in the background. Publishing before it is
    FINISHED fails with 'Media ID is not available' (code 9007)."""
    status_url = f"https://graph.facebook.com/v18.0/{container_id}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        res = requests.get(status_url, params={
            "fields": "status_code,status",
            "access_token": ACCESS_TOKEN,
        }).json()
        status = res.get("status_code")
        print(f"Container {container_id} status: {status}")
        if status == "FINISHED":
            return True
        if status in ("ERROR", "EXPIRED"):
            print("Container failed:", res)
            return False
        time.sleep(interval)
    print(f"Timed out waiting for container {container_id}")
    return False


def publish_carousel():
    slides = create_carousel_slides()
    print("Generated slides locally:", slides)
    
    if not ACCESS_TOKEN or not IG_USER_ID:
        print("Meta credentials missing!")
        sys.exit(1)

    # Get permanent public URLs via GitHub commit
    public_urls = commit_and_get_urls(slides)

    # Step 1: Create IG Container for each image in the carousel
    item_ids = []
    for img_url in public_urls:
        container_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
        payload = {
            "image_url": img_url,
            "is_carousel_item": "true",
            "access_token": ACCESS_TOKEN
        }
        res = requests.post(container_url, data=payload).json()
        if "id" in res:
            item_ids.append(res["id"])
            print(f"Created carousel item container: {res['id']}")
        else:
            print("Error creating item container:", res)
            sys.exit(1)

    for item_id in item_ids:
        if not wait_until_ready(item_id):
            sys.exit(1)

    # Step 2: Create Carousel Container
    carousel_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
    carousel_payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(item_ids),
        "caption": todays_caption(),
        "access_token": ACCESS_TOKEN
    }
    carousel_res = requests.post(carousel_url, data=carousel_payload).json()
    
    if "id" in carousel_res:
        creation_id = carousel_res["id"]
        print(f"Created main carousel container: {creation_id}")
        if not wait_until_ready(creation_id):
            sys.exit(1)

        # Step 3: Publish Carousel Container
        publish_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }
        pub_res = requests.post(publish_url, data=publish_payload).json()
        print("Publish Result:", pub_res)
        if "id" not in pub_res:
            sys.exit(1)
    else:
        print("Error creating carousel container:", carousel_res)
        sys.exit(1)

if __name__ == "__main__":
    publish_carousel()
