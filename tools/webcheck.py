import requests
from django.utils import timezone
from django.core.files.base import ContentFile
from .models import Tool, ToolMedia
import logging
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

def get_favicon(url, session):
    """
    Attempts to find and download the favicon.
    Returns (ContentFile, filename) or (None, None).
    """
    try:
        # 1. Try default location
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        favicon_url = urljoin(base_url, '/favicon.ico')
        
        response = session.get(favicon_url, timeout=5)
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            return convert_to_png(response.content)
            
        # 2. Try parsing HTML for link tag (skipped for now for speed, can assume default)
        return None, None
    except Exception as e:
        logger.error(f"Error fetching favicon for {url}: {e}")
        return None, None

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
            time.sleep(1) # Wait 1s as requested
            
            # Screenshot top 600px
            screenshot_bytes = page.screenshot(
                clip={'x': 0, 'y': 0, 'width': 1280, 'height': 600}
            )
            
            browser.close()
            return ContentFile(screenshot_bytes), "snapshot.png"
    except Exception as e:
        logger.error(f"Error taking snapshot for {url}: {e}")
        return None, None

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

def process_tool_webcheck(tool):
    """
    Runs the full webcheck for a single tool.
    Returns a dict of results.
    """
    results = {
        'tool': tool.name,
        'url_valid': False,
        'snapshot_taken': False,
        'favicon_updated': False,
        'meta_updated': False
    }
    
    session = requests.Session()
    
    # 1. Check URL
    is_valid, final_url, title, description = check_url(tool.website_url, session)
    tool.is_website_valid = is_valid
    tool.webcheck_last_run = timezone.now()
    
    if is_valid:
        results['url_valid'] = True
        
        # 2. Snapshot (only if NO media exists or force update - assuming only if working)
        # The prompt says: "create a snapshot so i can use it as image for the tool"
        # I'll add it as a new ToolMedia if none exists, or just do it.
        # Let's add it if no media of type 'image' exists.
        if not tool.media.filter(media_type='image').exists():
            content, filename = take_snapshot(tool.website_url)
            if content:
                # Create ToolMedia properly
                tm = ToolMedia(
                    tool=tool,
                    media_type='image',
                    alt_text=f"Snapshot of {tool.name}",
                    caption="Auto-generated snapshot"
                )
                tm.file.save(f"{tool.slug}_snapshot.png", content, save=True)
                
                # Also set as og_image if missing
                if not tool.og_image:
                     tool.og_image.save(f"{tool.slug}_og.png", content, save=True)
                     
                results['snapshot_taken'] = True
        
        # 3. Favicon (as Logo)
        if not tool.logo:
            content, filename = get_favicon(tool.website_url, session)
            if content:
                tool.logo.save(f"{tool.slug}_icon.png", content, save=False)
                results['favicon_updated'] = True

        # 4. Relevance (Cool things)
        # Suggest description update if empty?
        # Or just log it. For now, we update meta_title/desc if empty
        if not tool.meta_title and title:
            tool.meta_title = title[:200]
            results['meta_updated'] = True
        if not tool.meta_description and description:
            tool.meta_description = description
            results['meta_updated'] = True
            
    tool.save()
    return results
