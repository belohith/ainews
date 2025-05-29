# 📰 AI News Summarizer

This Streamlit application leverages a powerful pre-trained Large Language Model (LLM) to instantly summarize news articles. Users can input a URL to a news article, and the AI will generate a concise summary, making it easy to quickly grasp the main points without reading the entire piece.

## ✨ Features

* **Article Summarization:** Generates quick summaries of news articles from provided URLs.
* **Intuitive User Interface:** Built with Streamlit for a clean and interactive web application.
* **Local LLM Integration:** Utilizes a transformer-based model from Hugging Face's `transformers` library for efficient local inference.
* **Error Handling:** Provides informative feedback for invalid URLs or summarization issues.

## 🛠️ Technologies Used

* **Python**
* **Streamlit:** For building the interactive web application.
* **Hugging Face Transformers:** For the pre-trained summarization LLM (`sshleifer/distilbart-cnn-12-6`).
* **Requests:** For fetching web page content.
* **BeautifulSoup4:** For parsing HTML and extracting article text.
* **PyTorch (or TensorFlow):** Backend for the `transformers` library.

## 🚀 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourGitHubUsername/ai-news-summarizer.git](https://github.com/YourGitHubUsername/ai-news-summarizer.git)
    cd ai-news-summarizer
    ```
    (Replace `YourGitHubUsername` with your actual GitHub username and adjust repo name if different.)

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install streamlit transformers torch requests beautifulsoup4
    ```

4.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

5.  The application will open in your web browser, usually at `http://localhost:8501`.

## 💡 Usage

1.  Enter the URL of a news article in the input field.
2.  Click the "Summarize Article" button.
3.  View the generated summary and original article title.

## ✍️ Author

Lohith Bollineni

## 📄 License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).