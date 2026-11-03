import os
import requests
from generator import create_carousel_slides

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")
IG_USER_ID = os.getenv("IG_USER_ID")

CAPTION = "Master your wealth and build absolute financial freedom. 🇮🇳💼 #TheIndianRupees #PersonalFinance #WealthBuilding #InvestingIndia"

def publish_carousel():
    slides = create_carousel_slides()
    print("Prepared slides for publishing:", slides)
    # Meta Graph API container logic goes here using IG_USER_ID and ACCESS_TOKEN.

if __name__ == "__main__":
    publish_carousel()