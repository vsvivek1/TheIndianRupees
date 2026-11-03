import os
import requests
from generator import create_carousel_slides

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")

CAPTION = "Master your wealth and build absolute financial freedom. 🇮🇳💼 #TheIndianRupees #PersonalFinance #WealthBuilding #InvestingIndia"

def upload_to_free_host(image_path):
    # Uploads the generated slide to a temporary public host so Meta's crawler can access it
    with open(image_path, "rb") as f:
        files = {"image": f}
        response = requests.post("https://api.imgbb.com/1/upload", data={"key": "9659020197472856a0058b8f36c5897c"}, files=files)
        if response.status_code == 200:
            return response.json()["data"]["url"]
    return None

def publish_carousel():
    slides = create_carousel_slides()
    print("Generated slides locally:", slides)
    
    if not ACCESS_TOKEN or not IG_USER_ID:
        print("Meta credentials missing!")
        return

    # Upload slides to get public URLs required by Meta Graph API
    public_urls = []
    for slide in slides:
        print(f"Uploading {slide} for public URL...")
        url = upload_to_free_host(slide)
        if url:
            public_urls.append(url)
            print(f"Hosted URL: {url}")
        else:
            print(f"Failed to host {slide}")

    if len(public_urls) < len(slides):
        print("Error: Could not obtain public URLs for all slides.")
        return

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