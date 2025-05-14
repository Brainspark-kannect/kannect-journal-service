# app/utils/nlp.py
from textblob import TextBlob
from typing import Dict

def analyze_sentiment(text: str) -> Dict[str, any]:
    """
    Analyze sentiment of text using TextBlob
    Returns score (-1 to 1) and label (positive, neutral, negative)
    """
    analysis = TextBlob(text)
    score = analysis.sentiment.polarity
    
    if score > 0.1:
        label = "positive"
    elif score < -0.1:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "score": score,
        "label": label
    }

def extract_keywords(text: str, top_n: int = 5) -> list:
    """
    Extract key phrases or topics from text
    """
    blob = TextBlob(text)
    
    # Get noun phrases as potential keywords
    noun_phrases = blob.noun_phrases
    
    # Count word frequencies
    word_counts = {}
    for word in blob.words:
        # Normalize and filter short words
        word = word.lower()
        if len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Combine noun phrases and frequent words
    keywords = list(noun_phrases) + [word for word, count in sorted_words]
    
    # Return unique keywords
    unique_keywords = []
    for keyword in keywords:
        if keyword not in unique_keywords:
            unique_keywords.append(keyword)
    
    return unique_keywords[:top_n]
