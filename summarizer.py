from transformers import pipeline
import re
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objects as go

def summarize_reviews(reviews):
    if not reviews or reviews == ["No reviews found"]:
        return {
            "summary": "No reviews available to summarize.",
            "pros": ["• No positive reviews found"],
            "cons": ["• No negative reviews found"]
        }

    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        combined_reviews = " ".join(reviews)
        summary = summarizer(combined_reviews[:1024], max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        
        pros = []
        cons = []
        
        for review in reviews:
            review_lower = review.lower()
            
            if any(keyword in review_lower for keyword in [
                'good', 'great', 'excellent', 'perfect', 'bright', 'clear',
                'worth', 'value', 'affordable', 'quality', 'recommend'
            ]):
                
                point = re.sub(r'\s+', ' ', review).strip()
                if len(point) > 10:
                    pros.append(f"• {point[:100]}")
            
            
            if any(keyword in review_lower for keyword in [
                'bad', 'poor', 'issue', 'problem', 'not good', 'disappointed',
                'waste', 'expensive', 'defect', 'broken'
            ]):
                
                point = re.sub(r'\s+', ' ', review).strip()
                if len(point) > 10:
                    cons.append(f"• {point[:100]}")

       
        if len(pros) < 5:
            features = [
                f"• {feature.strip()}" for feature in re.split(r'[.,;]', combined_reviews)
                if any(keyword in feature.lower() for keyword in ['feature', 'support', 'include', 'provide'])
                and len(feature.strip()) > 10
            ]
            pros.extend(features)

        pros = list(dict.fromkeys(pros))[:5]  
        cons = list(dict.fromkeys(cons))[:5]  

        
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
    if not sentiments:
        return "<p>No sentiment data available</p>"
    
    # Count sentiments
    total = len(sentiments)
    positive = sum(1 for s in sentiments if s['compound'] > 0.05)
    negative = sum(1 for s in sentiments if s['compound'] < -0.05)
    neutral = total - positive - negative
    
    # Create data for pie chart
    values = [positive, negative, neutral]
    labels = ['Positive', 'Negative', 'Neutral']
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']

    # Create pie chart using Plotly
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=colors
    )])
    
    # Update layout
    fig.update_layout(
        title="Sentiment Distribution",
        annotations=[dict(text=f'Total Reviews: {total}', x=0.5, y=-0.1, showarrow=False)],
        width=600,
        height=400,
        showlegend=True
    )
    
    # Return the HTML representation of the chart
    return fig.to_html(full_html=False, include_plotlyjs=True)