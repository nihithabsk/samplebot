# from flask import Flask, render_template, request
# from scraper import scrape_flipkart, analyze_sentiment, summarize_reviews

# app = Flask(__name__)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     data = None
#     if request.method == "POST":
#         product_url = request.form.get("url")
#         if product_url:
#             data = scrape_flipkart(product_url)

#             # Ensure 'reviews' exists
#             reviews = data.get("reviews", ["No reviews found"])
#             sentiments = analyze_sentiment(reviews) if reviews and reviews != ["No reviews found"] else ["No sentiments found"]
#             summary = summarize_reviews(reviews)

#             data = {
#                 "title": data.get("title", "Title not found"),
#                 "price": data.get("price", "Price not found"),
#                 "sentiments": sentiments,
#                 "summary": summary,
#                 "reviews": reviews,
#                 "qandas": data.get("qandas", []),
#                 "image": data.get("image", [])
#             }

#     return render_template("index.html", data=data)

from flask import Flask, render_template, request, redirect, url_for
from scraper import scrape_flipkart, analyze_sentiment
from summarizer import summarize_reviews, generate_sentiment_chart
import json
from flask import jsonify

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        product_url = request.form.get("url")
        if product_url:
            return redirect(url_for("results", url=product_url))
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    reviews = data.get("reviews", "")
    
    if not reviews:
        return jsonify({"error": "No reviews provided."}), 400
    
    result = summarize_reviews(reviews)

    # Check if there's an error
    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)
@app.route("/results")
@app.route("/results")
def results():
    product_url = request.args.get("url")
    if not product_url:
        return redirect(url_for("index"))

    data = scrape_flipkart(product_url)
    reviews = data.get("reviews", ["No reviews found"])
    sentiments = analyze_sentiment(reviews) if reviews and reviews != ["No reviews found"] else []
    
    # Generate sentiment chart
    sentiment_chart = generate_sentiment_chart(sentiments)
    
    summary_data = summarize_reviews(reviews)
    
    data.update({
        "sentiments": sentiments,
        "sentiment_chart": sentiment_chart,
        "summary": summary_data.get("summary", "Unable to generate summary"),
        "pros": summary_data.get("pros", []),
        "cons": summary_data.get("cons", [])
    })

    return render_template("result.html", data=data)

    

if __name__ == "__main__":
    app.run(debug=True)

