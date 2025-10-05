import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text:str) -> str:
    ''' Analyze sentiment of given text  using VADER
    Return 'Positive' , 'Negative','Neutral'
    '''

    score = sia.polarity_score(text)
    compound = score["compound"]
    if  compound>=0.05:
        return "Positive"
    elif compound <=-0.05:
        return "Negative"
    else:
        return "Neutral"