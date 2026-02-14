import streamlit as st
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def show_news(uid):
    st.title("📰 Health News & Sentiment Insights")
    st.markdown("Latest health news with AI-powered sentiment analysis.")

    # 🔑 Your NewsAPI Key
    NEWS_API_KEY = "80804acdcc12426da84ab50c7e33f207"

    analyzer = SentimentIntensityAnalyzer()

    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "category": "health",
                "language": "en",
                "pageSize": 8,
                "apiKey": NEWS_API_KEY
            }
        )

        data = response.json()

        if data.get("status") != "ok":
            st.error("Failed to fetch news. Check your API key.")
            return

        articles = data.get("articles", [])

        if not articles:
            st.info("No news articles available.")
            return

        positive = 0
        neutral = 0
        negative = 0

        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "")
            url = article.get("url", "#")

            # 🔥 Sentiment Analysis
            sentiment_score = analyzer.polarity_scores(title)
            compound = sentiment_score["compound"]

            if compound >= 0.05:
                sentiment_label = "🟢 Positive"
                positive += 1
            elif compound <= -0.05:
                sentiment_label = "🔴 Negative"
                negative += 1
            else:
                sentiment_label = "🟡 Neutral"
                neutral += 1

            st.markdown("---")
            st.markdown(f"### [{title}]({url})")
            st.caption(f"Sentiment: {sentiment_label}")

            if description:
                st.write(description)

            if article.get("source"):
                st.caption(f"Source: {article['source']['name']}")

        # 📊 Sentiment Summary
        st.markdown("---")
        st.subheader("📊 Sentiment Overview")

        st.write(f"🟢 Positive: {positive}")
        st.write(f"🟡 Neutral: {neutral}")
        st.write(f"🔴 Negative: {negative}")

    except Exception as e:
        st.error(f"Error fetching news: {e}")
