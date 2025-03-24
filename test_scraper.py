import argparse
from scraper import scrape_flipkart

def test_scraper(save_results=False, debug_mode=False, headless=True):
    """
    Test the Flipkart scraper with a sample product URL
    
    Args:
        save_results (bool): Whether to save results to a file
        debug_mode (bool): Whether to enable debug mode
        headless (bool): Whether to run in headless mode
    """
    # Sample Flipkart iPhone URL
    url = "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"
    
    try:
        print(f"Testing scraper with URL: {url}")
        print(f"Debug mode: {debug_mode}, Headless: {headless}")
        
        # Call the scraper function
        result = scrape_flipkart(url, headless=headless, debug=debug_mode)
        
        # Print the results
        print("\n--- Scraping Results ---")
        print(f"Title: {result['title']}")
        print(f"Price: {result['price']}")
        print(f"Reviews found: {len(result['reviews'])}")
        
        # Print a sample of reviews if available
        if result['reviews']:
            print("\nSample reviews:")
            for i, review in enumerate(result['reviews'][:3]):
                print(f"{i+1}. {review}")
        
        # Save results if requested
        if save_results:
            import json
            with open('scraping_results.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\nResults saved to scraping_results.json")
            
        return result
        
    except Exception as e:
        print(f"Error testing scraper: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run the test with headless mode and debug enabled
    test_scraper(save_results=False, debug_mode=True, headless=True)

import sys
import traceback
import json
import time
import datetime
import os
from scraper import scrape_url

# The Flipkart iPhone URL to test
url = "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4?pid=MOBGTAGPTB3VS24W&lid=LSTMOBGTAGPTB3VS24WCTBCFM&marketplace=FLIPKART&q=iphone+15&store=tyy%2F4io&srno=s_1_1&otracker=AS_QueryStore_OrganicAutoSuggest_1_4_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_4_na_na_na&fm=organic&iid=en_pS2vJXJKE_3h_sJi8MyVT5z0YCE4fpYKeiBOmbw7VxdoOkuPj1ZJeGqx-Bo_dZrZGMR2mWpUjf14i-Dv0PyxGQ&ppt=hp&ppn=homepage&ssid=qn3ztbdvfk0000001742819193018&qH=2f54b45b321e3ae5"

def format_string_with_border(title, content=None, width=80):
    """Format a string with a nice border"""
    border = "=" * width
    title_line = f"== {title} ".ljust(width-1, "=") + "="
    
    result = f"\n{border}\n{title_line}\n{border}\n"
    if content:
        result += f"{content}\n{border}"
    
    return result

def save_results_to_file(result, filename=None):
    """Save results to a JSON file"""
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraping_results_{timestamp}.json"
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    file_path = os.path.join("results", filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return file_path

def test_scraper(save_results=True, debug_mode=True, headless=True):
    """Test the Selenium-based Flipkart scraper with error handling and output formatting"""
    print(format_string_with_border("FLIPKART SCRAPER TEST", f"URL: {url}"))
    
    start_time = time.time()
    result = None
    
    try:
        # Run the scraper function with specified parameters
        print("\n🚀 Starting Selenium scraper... (This may take a minute or two)")
        result = scrape_url(url, headless=headless, debug=debug_mode)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Print the results
        print(format_string_with_border("SCRAPING RESULTS", f"Time taken: {elapsed_time:.2f} seconds"))
        
        # Check if scraping was successful
        if not result.get('success', False):
            print(f"\n❌ Scraping completed with errors: {result.get('error', 'Unknown error')}")
        else:
            print(f"\n✅ Scraping completed successfully!")
        
        # Get the product data
        product_data = result.get('data', {}) if result.get('success', False) else result
        
        # Display product information
        print("\n📱 PRODUCT INFORMATION:")
        print(f"  Title: {product_data.get('title', 'Not found')}")
        print(f"  Price: {product_data.get('price', 'Not found')}")
        
        # Show rating if available
        rating = product_data.get('rating')
        if rating:
            print(f"  Rating: {rating}")
            
        # Show review count if available
        review_count = product_data.get('review_count')
        if review_count:
            print(f"  Review Count: {review_count}")
        
        # Handle reviews section
        reviews = product_data.get('reviews', [])
        
        if reviews:
            print(f"\n📝 REVIEWS: ({len(reviews)} found)")
            
            for i, review in enumerate(reviews, 1):
                if isinstance(review, str):
                    # String format review
                    review_text = review
                    formatted_review = f"  {i}. {review_text[:100]}{'...' if len(review_text) > 100 else ''}"
                    print(formatted_review)
                elif isinstance(review, dict):
                    # Dictionary format review (with text and sentiment)
                    review_text = review.get('text', 'No text')
                    sentiment = review.get('sentiment', {})
                    
                    # Format the review text
                    formatted_review = f"  {i}. {review_text[:100]}{'...' if len(review_text) > 100 else ''}"
                    print(formatted_review)
                    
                    # Show sentiment if available
                    if sentiment:
                        compound = sentiment.get('compound', 0)
                        sentiment_label = "Positive" if compound > 0.05 else "Negative" if compound < -0.05 else "Neutral"
                        print(f"     Sentiment: {sentiment_label} (Score: {compound:.2f})")
        else:
            print("\n⚠️ No reviews found")
        
        # Save results to file if requested
        if save_results and result:
            file_path = save_results_to_file(result)
            print(f"\n💾 Results saved to: {file_path}")
        
        return result
    
    except Exception as e:
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Print detailed error information
        print(format_string_with_border("ERROR OCCURRED", f"Time elapsed: {elapsed_time:.2f} seconds"))
        print(f"\n❌ Error type: {type(e).__name__}")
        print(f"❌ Error message: {str(e)}")
        
        # Print detailed traceback
        print("\n🔍 DETAILED TRACEBACK:")
        traceback.print_exc(file=sys.stdout)
        
        # Try to save any partial results if available
        
