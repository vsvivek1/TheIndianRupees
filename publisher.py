import os
import subprocess
import requests
from generator import create_carousel_slides

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")
REPO_NAME = os.getenv("GITHUB_REPOSITORY") # e.g. "vsvivek1/TheIndianRupees"

CAPTION = "Master your wealth and build absolute financial freedom. 🇮🇳💼 #TheIndianRupees #PersonalFinance #WealthBuilding #InvestingIndia"

def commit_and_get_urls(slides):
    # Configure git inside GitHub Actions runner
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"])
    
    # Add generated slides and commit them to main branch
    subprocess.run(["git", "add"] + slides)
    subprocess.run(["git", "commit", "-m", "Auto-generate daily carousel slides [skip ci]"])
    
    # Push back to repository
    push_res = subprocess.run(["git", "push"])
    if push_res.returncode != 0:
        print("Git push failed or nothing to commit.")
    
    # Generate official GitHub raw URLs for public Meta access
    public_urls = []
    for slide in slides:
        # GitHub raw URL format: https://raw.githubusercontent.com/USER/REPO/main/path/to/image.png
        raw_url = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{slide}"
        public_urls.append(raw_url)
        print(f"Public Raw URL: {raw_url}")
        
    return public_urls

def publish_carousel():
    slides = create_carousel_slides()
    print("Generated slides locally:", slides)
    
    if not ACCESS_TOKEN or not IG_USER_ID:
        print("Meta credentials missing!")
        return

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

    if not item_ids:
        print("No carousel items created.")
        return

    # Step 2: Create Carousel Container
    carousel_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
    carousel_payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(item_ids),
        "caption": CAPTION,
        "access_token": ACCESS_TOKEN
    }
    carousel_res = requests.post(carousel_url, data=carousel_payload).json()
    
    if "id" in carousel_res:
        creation_id = carousel_res["id"]
        print(f"Created main carousel container: {creation_id}")

        # Step 3: Publish Carousel Container
        publish_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }
        pub_res = requests.post(publish_url, data=publish_payload).json()
        print("Publish Result:", pub_res)
    else:
        print("Error creating carousel container:", carousel_res)

if __name__ == "__main__":
    publish_carousel()
