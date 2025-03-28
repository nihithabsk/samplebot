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

from flask import Flask, render_template, request, redirect, url_for, session,flash
from scraper import scrape_flipkart, analyze_sentiment
from summarizer import summarize_reviews, generate_sentiment_chart
import json
from flask import jsonify
import mysql.connector
import hashlib
from transformers import pipeline
import torch


app = Flask(__name__)
app.secret_key = 'qTUeDZmHDURGpynh0kxmpkCM0nNGNxl9'

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         product_url = request.form.get("url")
#         if product_url:
#             return redirect(url_for("results", url=product_url))
#     return render_template("index.html")

@app.route("/", methods=["GET"])
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    reviews = data.get("reviews", "")
    
    if not reviews:
        return jsonify({"error": "No reviews provided."}), 400
    
    result = summarize_reviews(reviews)

    
    if "error" in result:
        return jsonify(result), 500

    return jsonify(result)

# Add new imports at the top
from transformers import pipeline
import torch

# Modify the results route to store product data
@app.route("/results")
def results():
    if 'user' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))

    product_url = request.args.get("url")
    if not product_url:
        return redirect(url_for("product"))

    try:
        data = scrape_flipkart(product_url)
        reviews = data.get("reviews", ["No reviews found"])
        
        if reviews and reviews != ["No reviews found"]:
            sentiments = analyze_sentiment(reviews)
            sentiment_chart = generate_sentiment_chart(sentiments)
        else:
            sentiments = []
            sentiment_chart = generate_sentiment_chart(['Neutral'])
        
        summary_data = summarize_reviews(reviews)
        
        # Store all product data in session for chatbot
        session['product_data'] = {
            "title": data.get("title"),
            "price": data.get("price"),
            "reviews": reviews,
            "summary": summary_data.get("summary"),
            "pros": summary_data.get("pros"),
            "cons": summary_data.get("cons")
        }
        
        data.update({
            "sentiments": sentiments,
            "sentiment_chart": sentiment_chart,
            "summary": summary_data.get("summary", "Unable to generate summary"),
            "pros": summary_data.get("pros", []),
            "cons": summary_data.get("cons", [])
        })

        return render_template("result.html", data=data)
    except Exception as e:
        flash(f"Error processing the product: {str(e)}", "error")
        return redirect(url_for("product"))

# Add new route for chat functionality
@app.route('/chat', methods=['POST'])
def chat():
    if 'user' not in session:
        return jsonify({'error': 'Please login first'}), 401

    try:
        data = request.get_json()
        question = data.get('question')
        product_data = session.get('product_data', {})

        if not product_data:
            return jsonify({
                'answer': "Sorry, no product information is available. Please analyze a product first.",
                'confidence': 0,
                'source': 'No data'
            })

        # Initialize QA pipeline
        qa_model = pipeline('question-answering', model='deepset/roberta-base-squad2')
        
        # Create context from product information
        context = f"Product Name: {product_data.get('title', '')}\n"
        context += f"Price: {product_data.get('price', '')}\n"
        context += f"Product Summary: {product_data.get('summary', '')}\n"
        context += "Pros:\n" + "\n".join(product_data.get('pros', []))
        context += "\nCons:\n" + "\n".join(product_data.get('cons', []))
        context += "\nReviews:\n" + "\n".join(product_data.get('reviews', [])[:5])  # Include top 5 reviews
        
        # Get answer using the model
        answer = qa_model(question=question, context=context)
        
        return jsonify({
            'answer': answer['answer'],
            'confidence': round(answer['score'] * 100, 2),
            'source': 'Based on product information and reviews'
        })
        
    except Exception as e:
        return jsonify({
            'answer': "I apologize, but I couldn't process your question. Please try again.",
            'confidence': 0,
            'source': f'Error: {str(e)}'
        }), 500

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",  # Your MySQL password
        database="student_authen"
    )

# Home Route - Redirects to Login Page

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already exists! Please log in.", "error")
            return redirect('/login')

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                           (username, email, password))
            conn.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect('/login')
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('index.html', page='signup')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user'] = user[1]  # Store username in session
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "error")

    return render_template('index.html', page='login')


# Dashboard Route (After Login)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    else:
        flash("Please log in first!", "error")
        return redirect('/')

# Product Page (Takes Product Link)
@app.route('/product', methods=['GET', 'POST'])
def product():
    if 'user' not in session:
        flash("Please log in first!", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        product_link = request.form['product_link']
        return redirect(url_for('results', url=product_link))
    
    return render_template('index2.html')

# Chatbot Page (Final Destination)
@app.route('/chatbot')
def chatbot():
    if 'user' not in session:
        flash("Please log in first!", "error")
        return redirect('/login')
    
    return render_template('chatbot.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('product_link', None)
    flash("Logged out successfully!", "success")
    return redirect('/')

    

if __name__ == "__main__":
    app.run(debug=True)

