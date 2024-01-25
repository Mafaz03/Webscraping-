from textblob import TextBlob

def get_sentiment(paragraph):
    analysis = TextBlob(paragraph)
    sentiment_score = analysis.sentiment.polarity
    return sentiment_score

def get_emotion(sentiment_score):
    if sentiment_score < 0:
        emotion_category = "Sad or Angry"
    elif sentiment_score == 0:
        emotion_category = "Neutral or No Specific Emotion"
    else:
        emotion_category = "Happy or Positive"
    
    return emotion_category

# Example usage
paragraph = "According to Dubai Police, roads around Downtown and other popular locations will start closing around 4pm onwards while Sheikh Zayed Road will be closed from 9pm onwards. A total of 11,972 personnel, including 5,574 police officers, and 1,525 patrols, civil defence and ambulance vehicles, will be deployed across Dubai and Hatta to ensure the smooth management of the New Year's Eve 2024 celebrations."

sentiment_score = get_sentiment(paragraph)
emotion = get_emotion(sentiment_score)

print(f"Sentiment Score: {sentiment_score}")
print(f"Emotion: {emotion}")

