import os
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Target URL and output folder
url = "https://www.sekaipedia.org/wiki/List_of_cards"
save_dir = r"D:/GATLING TB/COCOde/Project Idle/gachademo/gachademo/images"
os.makedirs(save_dir, exist_ok=True)

# Launch Playwright to render JavaScript and get full HTML
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_selector("table.wikitable")  # Wait for table
    html = page.content()
    browser.close()

# Parse the rendered HTML with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
rows = soup.select("table.wikitable tbody tr")
print(f"✅ Found {len(rows)} card rows")

downloaded = 1
for row in rows:
    cols = row.find_all("td")
    if len(cols) < 2:
        continue

    img_tag = cols[1].find("img")
    if not img_tag:
        continue

    img_url = img_tag.get("data-src") or img_tag.get("src", "")
    if img_url.startswith("//"):
        img_url = "https:" + img_url

    # Convert to full-resolution image
    if "/thumb/" in img_url:
        parts = img_url.split("/thumb/")
        base = parts[0]
        rest = parts[1].split("/")
        real_path = "/".join(rest[:-1])  # remove '64px-<filename>'
        img_url = f"{base}/{real_path}"

    if "_thumbnail.png" not in img_url:
        continue

    original_name = os.path.basename(img_url).replace("64px-", "")  # e.g., Ichika_1_thumbnail.png
    name_only = original_name.replace("_thumbnail.png", "")         # → Ichika_1
    name_parts = name_only.split("_")                               # → ["Ichika", "1"]
    new_filename = f"thumbnail-{name_parts[0].lower()}-{name_parts[1]}.png"
    filename = os.path.join(save_dir, new_filename)


    try:
        img_response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"})
        if "image" not in img_response.headers.get("Content-Type", ""):
            print(f"⚠️ Skipped (not image): {img_url}")
            continue

        with open(filename, "wb") as f:
            f.write(img_response.content)
        print(f"⬇️ Saved: {filename.replace(os.sep, '/')}")
        downloaded += 1
    except Exception as e:
        print(f"⚠️ Error downloading {img_url}: {e}")

print(f"🎉 Done! {downloaded} thumbnails saved to:\n{save_dir}")