"""
Webcheck service for AI Robots.
Validates product URLs, captures screenshots, and fetches favicons.
Adapted from tools/webcheck.py.
"""

import requests
import logging
import time
from io import BytesIO
from urllib.parse import urljoin, urlparse

from django.utils import timezone
from django.core.files.base import ContentFile
from bs4 import BeautifulSoup
from PIL import Image
from playwright.sync_api import sync_playwright

from .models import Robot

logger = logging.getLogger(__name__)


def check_url(url, session):
    """
    Checks if the URL is accessible and not a parked domain.
    Returns (is_valid, final_url, title, description)
    """
    if not url:
        return False, None, "", ""
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        # Check for successful status code
        if response.status_code != 200:
            return False, response.url, "", ""

        # Basic check for parked domains
        text_lower = response.text.lower()
        parked_keywords = [
            'domain is for sale', 
            'buy this domain', 
            'domain parked', 
            'godaddy', 
            'namecheap', 
            'domain name registration',
            'sedo'
        ]
        
        if any(keyword in text_lower for keyword in parked_keywords) and len(response.text) < 5000:
             return False, response.url, "", ""
        
        # Metadata extraction
        title = ""
        description = ""
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else ""
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc:
                description = meta_desc.get('content', '').strip()
        except:
            pass

        return True, response.url, title, description

    except requests.RequestException:
        return False, None, "", ""


def convert_to_png(content):
    """
    Converts image content to PNG.
    """
    try:
        image = Image.open(BytesIO(content))
        output = BytesIO()
        image.save(output, format='PNG')
        return ContentFile(output.getvalue()), "favicon.png"
    except Exception as e:
        logger.error(f"Error converting favicon: {e}")
        return None, None


def get_favicon(url, session):
    """
    Attempts to find and download the favicon.
    Returns (ContentFile, filename) or (None, None).
    """
    try:
        # Try default location
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        favicon_url = urljoin(base_url, '/favicon.ico')
        
        response = session.get(favicon_url, timeout=5)
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            return convert_to_png(response.content)
            
        return None, None
    except Exception as e:
        logger.error(f"Error fetching favicon for {url}: {e}")
        return None, None


def take_snapshot(url):
    """
    Takes a snapshot of the website using Playwright.
    Returns (ContentFile, filename) or (None, None).
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 800})
            
            # Go to URL and wait
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(1)  # Wait 1s as per spec
            
            # Screenshot top 600px
            screenshot_bytes = page.screenshot(
                clip={'x': 0, 'y': 0, 'width': 1280, 'height': 600}
            )
            
            browser.close()
            return ContentFile(screenshot_bytes), "snapshot.png"
    except Exception as e:
        logger.error(f"Error taking snapshot for {url}: {e}")
        return None, None


def process_robot_webcheck(robot):
    """
    Runs the full webcheck for a single robot.
    Returns a dict of results.
    """
    results = {
        'robot': robot.name,
        'url_valid': False,
        'snapshot_taken': False,
        'favicon_updated': False,
        'meta_updated': False
    }
    
    session = requests.Session()
    
    # 1. Check URL (product_url)
    is_valid, final_url, title, description = check_url(robot.product_url, session)
    robot.is_product_url_valid = is_valid
    robot.webcheck_last_run = timezone.now()
    
    if is_valid:
        results['url_valid'] = True
        
        # 2. Snapshot (save to robot.image if empty)
        if not robot.image:
            content, filename = take_snapshot(robot.product_url)
            if content:
                robot.image.save(f"{robot.slug}_snapshot.png", content, save=False)
                results['snapshot_taken'] = True
        
        # 3. Favicon (save to robot.company.logo if empty)
        if robot.company and not robot.company.logo:
            content, filename = get_favicon(robot.product_url, session)
            if content:
                robot.company.logo.save(f"{robot.company.slug}_icon.png", content, save=True)
                results['favicon_updated'] = True

        # 4. Metadata (update if empty)
        if not robot.meta_title and title:
            robot.meta_title = title[:200]
            results['meta_updated'] = True
        if not robot.meta_description and description:
            robot.meta_description = description
            results['meta_updated'] = True
            
    robot.save()
    return results
