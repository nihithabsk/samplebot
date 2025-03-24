from flask import Flask, render_template, request
from scraper import scrape_flipkart, analyze_sentiment, summarize_reviews

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    if request.method == "POST":
        product_url = request.form.get("url")
        if product_url:
            data = scrape_flipkart(product_url)

            # Ensure 'reviews' exists
            reviews = data.get("reviews", ["No reviews found"])
            sentiments = analyze_sentiment(reviews) if reviews and reviews != ["No reviews found"] else ["No sentiments found"]
            summary = summarize_reviews(reviews)

            data = {
                "title": data.get("title", "Title not found"),
                "price": data.get("price", "Price not found"),
                "sentiments": sentiments,
                "summary": summary,
                "reviews": reviews,
                "qandas": data.get("qandas", [])
            }

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
