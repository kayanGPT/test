import openai
from textblob import TextBlob

class ContentGenerator:
    def __init__(self, openai_api_key):
        openai.api_key = openai_api_key
    
    def generate_content(self, transcription):
        try:
            # Generate caption
            caption_prompt = f"Based on the following transcription, write an engaging and concise social media caption that summarizes the main points and encourages viewers to watch the video:\n\n{transcription}"
            caption_response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": caption_prompt}],
                max_tokens=150
            )
            caption = caption_response.choices[0].message['content'].strip()
            
            # Analyze sentiment and extract main topics
            sentiment, topics = self.analyze_content(transcription)
            
            # Generate hashtags
            hashtag_prompt = f"""
            Based on the following transcription, sentiment analysis, and main topics, generate 10 relevant and trending hashtags for social media platforms. The hashtags should be popular, related to the content, and include a mix of general and specific tags:

            Transcription: {transcription}

            Sentiment: {sentiment}
            Main Topics: {', '.join(topics)}

            Please provide a list of 10 hashtags, each starting with '#'.
            """
            hashtag_response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": hashtag_prompt}],
                max_tokens=100
            )
            hashtags = hashtag_response.choices[0].message['content'].strip()
            
            return caption, hashtags
        except Exception as e:
            print(f"Content generation error: {str(e)}")
            return "", ""
    
    def analyze_content(self, transcription):
        # Perform sentiment analysis
        blob = TextBlob(transcription)
        sentiment = "positive" if blob.sentiment.polarity > 0 else "negative" if blob.sentiment.polarity < 0 else "neutral"
        
        # Extract main topics
        topic_prompt = f"Extract the main topics or themes from the following transcription. Provide a list of 3-5 key topics:\n\n{transcription}"
        topic_response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": topic_prompt}],
            max_tokens=50
        )
        topics = topic_response.choices[0].message['content'].strip().split('\n')
        topics = [topic.strip('- ') for topic in topics]
        
        return sentiment, topics
