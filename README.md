# Basalam AI Agent

Basalam AI Agent is a Persian-language ai assistant for the Basalam marketplace. This project uses llm and LangChain to allow users to search for products using conversational queries, apply filters like maximum price, and receive results including product images, prices, and direct purchase links—all within a simple Streamlit web interface.

## Features

* **Conversational Search:** Understands and processes Persian-language queries, even when phrased casually or ambiguously.
* **Product Search via Basalam API:** Uses Basalam's public search API to fetch real-time product data.
* **Price Filtering:** Supports queries that include a maximum price limit.
* **Structured Product Display:** Returns product name, price (in Toman), rating, seller info, and a direct link.
* **Streamlit UI:** A clean and minimal web interface that presents results attractively.

## Example Query

**User input:**
```sh
کفش مردانه زیر ۸۰۰ هزار تومان
```

**Expected response:**

Product list with names, prices, images, and links filtered to a max of 800,000 Toman.

## How to Run Locally

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/m451h/basalamAiAgent.git](https://github.com/m451h/basalamAiAgent.git)
    cd basalamAiAgent
    ```

2.  **Install dependencies**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Add your API keys**
    Create a `.env` file in the project root with the following variables:
    ```dotenv
    OPENAI_API_KEY=your_groq_or_openai_key
    OPENAI_API_BASE=[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)
    ```

4.  **Run the app**
    ```bash
    streamlit run app.py
    ```

## Deployment


`https://basalamaiagent.onrender.com/` 

## Project Structure
```bash
├── app.py               # Streamlit frontend
├── chat.py              # LangChain agent and logic
├── basalam_search.py    # Tool for calling Basalam API
├── prompts/
│   └── base.txt         # Main system prompt for the agent
├── requirements.txt     # Python dependencies
└── .env                 # API key environment variables (not committed)

```
## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author

Created by m451h
