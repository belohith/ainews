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
        # Newspaper3k often identifies the main text.
        # You can add more checks here if needed (e.g., minimum article.text length)
        if article.text and len(article.text) > 200: # Heuristic for meaningful article
            return article.text
        else:
            return None # Not a typical article or not enough content
    except Exception as e:
        # print(f"Error with newspaper3k for {url}: {e}") # For debugging
        return None

# --- AI Summarization Function (remains the same) ---
@st.cache_data
def summarize_text(text, _summarizer_pipeline):
    if not text or len(text.strip()) < 50:
        return "Not enough content to generate a summary."
    try:
        summary = _summarizer_pipeline(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        return summary
    except Exception as e:
        return f"Could not summarize this article due to an AI model error: {e}"

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

            # --- REMAINS THE SAME FOR NOW, WILL CHANGE FOR SINGLE COLUMN BELOW ---
            # cols = st.columns(2)
            # col_idx = 0

            for i, article in enumerate(display_headlines):
                # with cols[col_idx % 2]: # This line will be removed for single column
                # Use a container for each article card for better visual grouping
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
                            # Call the new newspaper3k function
                            article_content = get_article_content_newspaper(article['link'])
                            if article_content:
                                summary = summarize_text(article_content, summarizer_pipeline)
                                st.session_state[summary_key] = f"**AI Summary:** {summary}"
                            else:
                                st.session_state[summary_key] = "Could not retrieve meaningful article content for summarization (link may not be a standard article)."
                        st.rerun()

                st.markdown("") # Add a small gap between article containers
                # col_idx += 1 # This line will be removed for single column
        else:
            st.warning("No headlines found or an error occurred. Please try again later.")
    elif news_source == "Select a source":
        st.info("Please select a news source from the sidebar to view headlines.")

if __name__ == "__main__":
    main()