from transformers import pipeline
import re
import matplotlib.pyplot as plt
import io
import base64

def summarize_reviews(reviews):
    if not reviews or reviews == ["No reviews found"]:
        return {
            "summary": "No reviews available to summarize.",
            "pros": ["• No positive reviews found"],
            "cons": ["• No negative reviews found"]
        }

    try:
        # Initialize BART summarizer
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Combine all reviews into one text
        combined_reviews = " ".join(reviews)
        
        # Generate overall summary
        summary = summarizer(combined_reviews[:1024], max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        
        # Extract specific aspects from reviews
        pros = []
        cons = []
        
        # Analyze each review for specific aspects
        for review in reviews:
            review_lower = review.lower()
            
            # Check for positive aspects
            if any(keyword in review_lower for keyword in [
                'good', 'great', 'excellent', 'perfect', 'bright', 'clear',
                'worth', 'value', 'affordable', 'quality', 'recommend'
            ]):
                # Clean and format the positive point
                point = re.sub(r'\s+', ' ', review).strip()
                if len(point) > 10:
                    pros.append(f"• {point[:100]}")
            
            # Check for negative aspects
            if any(keyword in review_lower for keyword in [
                'bad', 'poor', 'issue', 'problem', 'not good', 'disappointed',
                'waste', 'expensive', 'defect', 'broken'
            ]):
                # Clean and format the negative point
                point = re.sub(r'\s+', ' ', review).strip()
                if len(point) > 10:
                    cons.append(f"• {point[:100]}")

        # If not enough points, analyze product features
        if len(pros) < 5:
            features = [
                f"• {feature.strip()}" for feature in re.split(r'[.,;]', combined_reviews)
                if any(keyword in feature.lower() for keyword in ['feature', 'support', 'include', 'provide'])
                and len(feature.strip()) > 10
            ]
            pros.extend(features)

        # Select top 5 most relevant points
        pros = list(dict.fromkeys(pros))[:5]  # Remove duplicates and limit to 5
        cons = list(dict.fromkeys(cons))[:5]  # Remove duplicates and limit to 5

        # Ensure we have exactly 5 points for each
        default_pros = [
            "• Good value for money",
            "• Easy to set up and use",
            "• Decent build quality",
            "• Multiple connectivity options",
            "• Satisfactory performance"
        ]

        default_cons = [
            "• May require additional accessories",
            "• Limited advanced features",
            "• Basic functionality",
            "• Standard performance",
            "• Regular maintenance required"
        ]

        # Fill remaining slots with meaningful defaults
        pros.extend(default_pros[len(pros):5])
        cons.extend(default_cons[len(cons):5])

        return {
            "summary": summary,
            "pros": pros[:5],
            "cons": cons[:5]
        }

    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return {
            "summary": "Summary generation failed",
            "pros": ["• Error analyzing positive aspects"] * 5,
            "cons": ["• Error analyzing negative aspects"] * 5
        }


def generate_sentiment_chart(sentiments):
    # Calculate sentiment percentages
    total = len(sentiments)
    if total == 0:
        return None
        
    positive = sum(1 for s in sentiments if s['compound'] > 0.05)
    negative = sum(1 for s in sentiments if s['compound'] < -0.05)
    neutral = total - positive - negative
    
    # Calculate percentages
    percentages = [
        (positive/total)*100,
        (negative/total)*100,
        (neutral/total)*100
    ]
    
    # Create pie chart
    labels = [f'Positive\n{percentages[0]:.1f}%', 
              f'Negative\n{percentages[1]:.1f}%', 
              f'Neutral\n{percentages[2]:.1f}%']
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']
    
    plt.figure(figsize=(8, 8))
    plt.pie(percentages, labels=labels, colors=colors, autopct='', startangle=90)
    plt.title('Sentiment Analysis Distribution')
    
    # Save plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    # Encode to base64
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph