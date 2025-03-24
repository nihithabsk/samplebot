
from playwright.sync_api import sync_playwright
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import random
import time
import os
import json
from datetime import datetime

def create_debug_folder():
    """Create a folder for debug outputs"""
    debug_dir = "debug_output"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = f"{debug_dir}/{timestamp}"
    os.makedirs(session_dir, exist_ok=True)
    return session_dir

def random_sleep(min_seconds=1, max_seconds=4):
    """Sleep for a random amount of time to mimic human behavior"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def apply_stealth_techniques(page):
    """Apply basic techniques to make the browser look more human-like"""
    # Simple script to hide automation indicators
    page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false
    });
    """)
    
    return page


def create_debug_folder():
    return "./debug"

def scrape_flipkart(product_url, debug_mode=True):
    browser = None
    debug_dir = create_debug_folder() if debug_mode else None

    try:
        print(f"Starting to scrape Flipkart URL: {product_url}")
        with sync_playwright() as p:
            print("Launching browser...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                    '--no-sandbox'
                ]
            )

            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0"
            ]

            page = browser.new_page(
                user_agent=random.choice(user_agents),
                viewport={"width": 1920, "height": 1080},
                locale="en-IN",
                timezone_id="Asia/Kolkata",
            )

            
            page = apply_stealth_techniques(page)

            print("Navigating to Flipkart homepage...")
            page.goto("https://www.flipkart.com/", timeout=30000)
            random_sleep(2, 4)

            print("Now navigating to product page...")
            page.goto(product_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)

            print("Extracting product information...")

            title_selectors = ["span.VU-ZEz","div._6EBuvT","span.VU-ZEz","span.B_NuCI", "h1.yhB1nd", "h1[data-testid='product-title']"]
            title = "Title not found"
            for selector in title_selectors:
                title_element = page.locator(selector)
                if title_element.count() > 0:
                    title = title_element.text_content().strip()
                    break

            price_selectors = ["div.Nx9bqj CxhGGd","div.Nx9bqj CxhGGd","div.UOCQB1","div._30jeq3._1_WHN1", "div._30jeq3", "[data-testid='price-display']"]
            price = "Price not found"
            for selector in price_selectors:
                price_element = page.locator(selector)
                if price_element.count() > 0:
                    price = price_element.text_content().strip()
                    break

            review_selectors = ["cPHDOP col-12-12","div.DOjaWF gdgoEp","div.col pPAw9M","_8-rIO3","div.DOjaWF.gdgoEp","div.t-ZTKy", "div._16PBlm", "div[data-testid='review-container']"]
            reviews = []
            for selector in review_selectors:
                review_elements = page.locator(selector).all()
                if review_elements:
                    reviews = [elem.text_content().strip() for elem in review_elements if len(elem.text_content().strip()) > 5]
                    break
                    

            if not reviews:
                reviews = ["No reviews found"]

            qandas = ["div.cPHDOP col-12-12","div.wys2hv _43gOsC"]
            ans =[]
            for selector in qandas:
                qanda_elements = page.locator(selector).all()
                if qanda_elements:
                    ans = [elem.text_content().strip() for elem in qanda_elements if len(elem.text_content().strip()) > 5]
                    break 
            img = ["div._8id3KM _1NsuIS","div._8id3KM","img.DByuf4.IZexXJ.jLEJ7H","div.vU5WPQ","div._4WELSP _6lpKCl"]
            
            image_url = "Image not found"
            for selector in img:
                try:
                    image_element = page.locator(selector).first
                    if image_element:
                        image_url = image_element.get_attribute("src")
                        if image_url:
                            break
                except:
                    continue


            browser.close()
            return {"title": title or "title not found", "price": price or "price not found", "reviews": reviews if reviews else ["No reviews found"], "qandas": ans if qandas else [], "image": image_url if img else "Image not found"}

    except Exception as e:
        print(f"Error scraping Flipkart: {e}")
        try:
            browser.close()
        except Exception as close_error:
            print(f"Error closing browser: {close_error}")

        return {"title": "Error", "message": str(e)}

def analyze_sentiment(reviews):
    analyzer = SentimentIntensityAnalyzer()
    return [analyzer.polarity_scores(review) for review in reviews]

# def summarize_reviews(reviews):
#     summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
#     if len(" ".join(reviews)) < 20:
#         return "Not enough data to summarize."
    
#     return summarizer(" ".join(reviews)[:1024], max_length=150, min_length=20, do_sample=False)[0]["summary_text"]
