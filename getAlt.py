import sys
import os
import requests
import math
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image  # Added import for Pillow
import io
def is_base64_image(img_tag):
    return img_tag.startswith('data:image')

def is_svg_image(img_tag):
    return img_tag.endswith('.svg') or img_tag.startswith('data:image/svg+xml')

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def get_image_size(url):
    try:
        response = requests.head(url)
        if response.status_code == 200:
            content_length = response.headers.get('content-length')
            return convert_size(int(content_length)) if content_length else None
    except requests.exceptions.RequestException as e:
        print(f'Error retrieving image size: {e}')
    return None
def get_image_dimensions(img_url):
    try:
        response = requests.get(img_url, stream=True)
        response.raise_for_status()
        with Image.open(io.BytesIO(response.content)) as img:
            width, height = img.size
            return f"{width}x{height}"
    except Exception as e:
        print(f'Error retrieving image dimensions: {e}')
    return None

def extract_alt_text(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img', src=lambda x: x and not (x.endswith(('.gif', '.svg')) or is_base64_image(x) or is_svg_image(x)))

        html_content = '<html><head><title>Image Alt Text</title></head><body>'
        total_images = 0

        for img_tag in img_tags:
            if img_tag.find_parent('p'):
                continue

            img_src = urljoin(url, img_tag['src'])
            alt_text = img_tag.get('alt', 'No Alt Text')
            image_size = get_image_size(img_src)
            image_dimensions = get_image_dimensions(img_src)

            html_content += f'<img src="{img_src}" alt="{alt_text}"><br>'
            html_content += f'Alt Text: {alt_text}<br>'
            html_content += f'Image Size: {image_size}<br>' if image_size else 'Image Size: Not Available<br>'
            html_content += f'Image Dimensions: {image_dimensions}<br>' if image_dimensions else 'Image Dimensions: Not Available<br>'
            html_content += f'Image Name: {os.path.basename(img_src)}<br>'
            html_content += '<hr>'
            total_images += 1

        html_content += f'</body></html>'
        file_path = os.path.expanduser('~/storage/downloads/image_alt_text.html')

        with open(file_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        print(f'HTML page with {total_images} images, alt text, image size, dimensions, and name created: {file_path}')
    else:
        print(f'Failed to retrieve content. Status Code: {response.status_code}')

if len(sys.argv) == 2:
    url_to_scrape = sys.argv[1]
    extract_alt_text(url_to_scrape)
else:
    print('Please provide a URL as a command-line argument.')
