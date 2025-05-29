import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from newspaper import Article # Import Article from newspaper3k

# --- Configuration ---
SUMMARIZER_MODEL = "sshleifer/distilbart-cnn-12-6"

# --- Caching the Model Loading ---
@st.cache_resource
def load_summarizer_model():
    with st.spinner("Loading AI summarization model... This might take a minute the first time."):
        summarizer = pipeline("summarization", model=SUMMARIZER_MODEL)
        st.success("AI model loaded!")
    return summarizer

# --- Web Scraping Function (Hacker News Headlines - remains the same) ---
@st.cache_data(ttl=3600)
def get_hacker_news_headlines():
    url = "https://news.ycombinator.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        headlines = []
        for span_tag in soup.find_all('span', class_='titleline'):
            link_tag = span_tag.find('a')
            if link_tag:
                title = link_tag.get_text(strip=True)
                href = link_tag.get('href')
                if title and href and href.startswith('http'):
                    headlines.append({"title": title, "link": href})
        return headlines
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch news headlines: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred during headline scraping: {e}")
        return []

# --- Article Content Scraping with newspaper3k ---
@st.cache_data(ttl=3600)
def get_article_content_newspaper(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        # Check if the article has sufficient text and is likely a news article
        if article.text and len(article.text) > 200: # Heuristic for meaningful article
            return article.text
        else:
            return None # Not a typical article or not enough content
    except Exception as e:
        return None

# --- AI Summarization Function ---
@st.cache_data(show_spinner="Summarizing article...")
def summarize_text(text, _summarizer): # Keep the underscore as _summarizer is unhashable
    # We need to make sure the input text is truncated to the model's max input length
    # The distilbart-cnn-12-6 model has a max input of 1024 tokens.
    # It's good practice to provide a reasonable max_length for the output as well.
    try:
        summary = _summarizer(
            text, # 'text' is hashable, so no underscore needed here
            max_length=150, # Max length of the output summary
            min_length=30,  # Min length of the output summary
            do_sample=False,
            truncation=True # CRITICAL: This tells the tokenizer to truncate the input
                            # to the model's maximum accepted length (e.g., 1024 tokens).
        )[0]['summary_text']
        return summary
    except Exception as e:
        st.error(f"AI summarization failed with an internal model error: {e}")
        # Optionally, you can print the length of the text for debugging
        # st.write(f"Debug: Input text length was {len(text)} characters.")
        return "Could not summarize this article due to an AI model error. The article might be too complex or too long for the model."



# --- Main Streamlit Application ---
def main():
    st.set_page_config(
        page_title="AI News Summarizer",
        page_icon="📰",
        layout="wide"
    )

    st.title("📰 AI News Summarizer Dashboard")

    st.markdown("""
    Welcome to your **AI News Summarizer**!
    Select a news source from the sidebar and get instant summaries of top headlines.
    """)

    # --- ADD THIS NEW DISCLAIMER HERE ---
    st.info("""
    **Important Note:** This app currently fetches headlines from **Hacker News (Y Combinator)** only.
    Please be aware that Hacker News often links to discussions, blog posts, or technical papers,
    not always traditional news articles. For these types of links, an AI summary may not be possible or relevant.
    More diverse news sources will be added in future updates!
    """)
    # --- END OF DISCLAIMER ---

    summarizer_pipeline = load_summarizer_model()

    # --- Sidebar for settings ---
    st.sidebar.header("Settings")
    st.sidebar.markdown("Configure your news feed here.")

    news_source = st.sidebar.selectbox(
        "Choose a News Source",
        ["Select a source", "Hacker News"]
    )

    num_articles_to_display = st.sidebar.slider(
        "Number of articles to display",
        min_value=1, max_value=20, value=5
    )

    if news_source == "Hacker News":
        st.subheader(f"Latest Headlines from {news_source}")
        with st.spinner("Fetching headlines..."):
            headlines = get_hacker_news_headlines()

        if headlines:
            display_headlines = headlines[:num_articles_to_display]

            for i, article in enumerate(display_headlines):
                with st.container(border=True): # border=True gives a nice visual separation
                    st.markdown(f"#### {article['title']}")
                    st.markdown(f"**Link:** [Read Full Article]({article['link']})")

                    summary_key = f"summary_{i}"
                    if summary_key not in st.session_state:
                        st.session_state[summary_key] = "Click 'Summarize' to get an AI-generated summary."

                    st.info(st.session_state[summary_key])

                    summarize_button_key = f"summarize_btn_{i}"
                    if st.button("Summarize", key=summarize_button_key):
                        with st.spinner("Getting article content and summarizing..."):
                            article_content = get_article_content_newspaper(article['link'])
                            if article_content:
                                summary = summarize_text(article_content, summarizer_pipeline)
                                st.session_state[summary_key] = f"**AI Summary:** {summary}"
                            else:
                                st.session_state[summary_key] = "Could not retrieve meaningful article content for summarization (link may not be a standard article)."
                        st.rerun()

                st.markdown("") # Add a small gap between article containers
        else:
            st.warning("No headlines found or an error occurred. Please try again later.")
    elif news_source == "Select a source":
        st.info("Please select a news source from the sidebar to view headlines.")

if __name__ == "__main__":
    main()