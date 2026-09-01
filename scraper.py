import re
import logging
from dataclasses import dataclass
from typing import List, Optional
import db
from playwright.sync_api import sync_playwright, Locator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class Product:
    item_id: str
    title: str
    price_raw: str
    price_numeric: Optional[int]
    url: str
    category: str

def parse_price(price_str: str) -> Optional[int]:
    if not price_str:
        return None
    cleaned = re.sub(r"\D", "", price_str)    
    if not cleaned:
        logger.warning(f"Could not parse price from string: {price_str}")
        return None
    try:
        return int(cleaned)
    except ValueError:
        logger.warning(f"Failed to convert cleaned price to int: {price_str}")
        return None
    
def extract_product(item: Locator, category: str) -> Optional[Product]:
    try:
        item_id = item.get_attribute("data-item-id")
        title = item.locator("[class*='RfADt'] a").get_attribute("title")
        price_raw = item.locator("[class*='ooOxS']").inner_text()
        url = item.locator("[class*='RfADt'] a").get_attribute("href")
        
        if url and url.startswith("/"):
            url = f"https://www.daraz.com.np{url}"
            
        price_numeric = parse_price(price_raw)
        
        return Product(
            item_id=item_id or "unknown",
            title=title or "No title",
            price_raw=price_raw or "",
            price_numeric=price_numeric,
            url=url or "",
            category=category
        )
    except Exception as e:
        logger.error(f"Failed to extract product: {e}")
        return None

def scrape_daraz_category(category_url: str, category_name: str, limit: int = 5) -> List[Product]:
    products = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        logger.info(f"Navigating to {category_url}")
        page.goto(category_url, wait_until="networkidle")
        
        page.wait_for_selector("div[data-qa-locator='product-item']", timeout=15000)
        
        items = page.locator("div[data-qa-locator='product-item']")
        count = items.count()
        logger.info(f"Found {count} product cards. Extracting up to {limit}.")
        
        for i in range(min(limit, count)):
            item = items.nth(i)
            product = extract_product(item, category_name)
            if product:
                products.append(product)
                logger.info(f"Extracted: {product.title} -> {product.price_numeric}")
        
        browser.close()
    
    return products

if __name__ == "__main__":
    results = scrape_daraz_category(
        category_url="https://www.daraz.com.np/smartphones/",
        category_name="smartphones",
        limit=5
    )
    
    for p in results:
        db.insert_data(p.item_id, p.title, p.url, p.price_numeric)