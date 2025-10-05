import nltk
import os

# DEBUG: Print all paths
print("=== NLTK DEBUG ===")
print("NLTK_DATA env:", os.getenv('NLTK_DATA'))
print("Current NLTK paths:", nltk.data.path)

# Set NLTK data path - FORCE the Docker path
docker_path = '/usr/local/nltk_data'
nltk.data.path.append(docker_path)
print(f"Force added Docker path: {docker_path}")

# Check if the path exists and what's in it
if os.path.exists(docker_path):
    print(f"Docker path exists: {docker_path}")
    sentiment_dir = os.path.join(docker_path, 'sentiment')
    if os.path.exists(sentiment_dir):
        print("Files in sentiment directory:", os.listdir(sentiment_dir))
else:
    print(f"Docker path does NOT exist: {docker_path}")

try:
    # Try to use VADER sentiment analyzer
    nltk.data.find('sentiment/vader_lexicon')
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    print("✅ Using VADER sentiment analyzer")
except LookupError as e:
    print(f"❌ VADER not found: {e}")
    # Fallback to simple rule-based analyzer
    print("NLTK vader_lexicon not found, using fallback sentiment analysis")
    
    class SimpleSentimentAnalyzer:
        def __init__(self):
            self.positive_words = {
                'good', 'great', 'awesome', 'excellent', 'amazing', 'love', 'best', 
                'fantastic', 'wonderful', 'brilliant', 'outstanding', 'superb', 'perfect',
                'enjoyed', 'liked', 'beautiful', 'masterpiece', 'impressive', 'incredible',
                'favorite', 'recommend', 'enjoyable', 'pleasantly', 'surprised', 'love',
                'fantastic', 'amazing', 'brilliant', 'outstanding'
            }
            self.negative_words = {
                'bad', 'terrible', 'awful', 'poor', 'hate', 'worst', 'boring',
                'horrible', 'disappointing', 'waste', 'rubbish', 'stupid', 'dull',
                'annoying', 'hated', 'dislike', 'unfortunately', 'weak', 'mess',
                'confusing', 'predictable', 'cliche', 'pointless', 'hate', 'terrible',
                'awful', 'horrible', 'disappointing'
            }
            self.intensifiers = {
                'absolutely', 'extremely', 'incredibly', 'totally', 'completely',
                'utterly', 'especially', 'particularly', 'very', 'really', 'so'
            }
        
        def polarity_scores(self, text):
            text_lower = text.lower()
            words = text_lower.split()
            
            positive_score = 0
            negative_score = 0
            total_words = len(words)
            
            for i, word in enumerate(words):
                # Check for positive words
                if word in self.positive_words:
                    positive_score += 1
                    # Check for intensifiers before the word
                    if i > 0 and words[i-1] in self.intensifiers:
                        positive_score += 0.5
                
                # Check for negative words
                if word in self.negative_words:
                    negative_score += 1
                    # Check for intensifiers before the word
                    if i > 0 and words[i-1] in self.intensifiers:
                        negative_score += 0.5
            
            # Calculate compound score
            if total_words == 0:
                compound = 0
            else:
                # Normalize scores and create compound
                pos_norm = positive_score / total_words
                neg_norm = negative_score / total_words
                compound = pos_norm - neg_norm
            
            return {
                'neg': min(negative_score / max(total_words, 1), 1.0),
                'neu': max(1 - (positive_score + negative_score) / max(total_words, 1), 0),
                'pos': min(positive_score / max(total_words, 1), 1.0),
                'compound': compound
            }
    
    sia = SimpleSentimentAnalyzer()

def predict_sentiment(text):
    """
    Analyze sentiment using VADER or fallback method
    Returns sentiment and confidence score
    """
    scores = sia.polarity_scores(text)
    
    # Determine sentiment based on compound score
    compound = scores['compound']
    
    if compound >= 0.05:
        sentiment = "positive"
        confidence = min(compound, 1.0)
    elif compound <= -0.05:
        sentiment = "negative"
        confidence = min(abs(compound), 1.0)
    else:
        sentiment = "neutral"
        confidence = 1 - abs(compound)
    
    return sentiment, round(confidence, 4)