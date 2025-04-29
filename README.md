# Basalam AI Shopping Assistant

Basalam AI Shopping Assistant is an **AI-powered conversational agent** designed to assist Persian-speaking users in finding products on the Basalam marketplace. Unlike a traditional search engine, this agent uses **natural language understanding** to interpret user queries and provide personalized, structured responses. It leverages **LangChain** and **Large Language Models (LLMs)** to process conversational inputs and interact with the Basalam API for real-time product data.


## Testing Demo

You can try out a live demo of the Basalam AI Shopping Assistant at the following link:

[Basalam AI Shopping Assistant Demo](https://basalamaiagent.onrender.com)
![alt text](image-1.png)

## Features

- **Conversational AI**: Understands Persian-language queries, even if phrased casually or ambiguously.
- **Smart Filtering**: Supports advanced filters such as maximum price, minimum rating, and seller city.
- **Real-Time Data**: Fetches up-to-date product information from the Basalam marketplace.
- **Structured Responses**: Displays product details like name, price, rating, seller info, and direct purchase links in a user-friendly format.
- **Streamlit UI**: A clean and interactive web interface for seamless user interaction.

## Example Queries

Here are some examples of how you can interact with the AI agent:

1. **Basic Query**:
    ```
    کفش مردانه زیر ۸۰۰ هزار تومان
    ```
    **Response**: A list of men's shoes priced below 800,000 Toman.

2. **Using Filters**:
    - **Maximum Price**:
        ```
        عسل طبیعی زیر ۵۰۰ هزار تومان
        ```
        **Response**: A list of natural honey products priced below 500,000 Toman.

    - **Vendor City**:
        ```
        کیف زنانه از فروشندگان تهران
        ```
        **Response**: Women's bags sold by vendors in Tehran.

    - **Minimum Rating**:
        ```
        شلوار مردانه با امتیاز بالای ۴
        ```
        **Response**: Men's pants with a rating of 4 or higher.

    - **Combined Filters**:
        ```
        عطر زنانه زیر ۱ میلیون تومان از فروشندگان مشهد با امتیاز بالای ۴.۵
        ```
        **Response**: Women's perfumes priced below 1,000,000 Toman, sold by vendors in Mashhad, with a rating of 4.5 or higher.

3. **Ambiguous Query**:
    ```
    بهترین هدیه برای تولد زیر ۳۰۰ هزار تومان
    ```
    **Response**: Suggestions for birthday gifts priced below 300,000 Toman.

4. **Messaging Sellers**:
    ```
    می‌خواهم به فروشنده پیام بدهم که آیا این محصول موجود است؟
    ```
    **Response**: The AI agent will return the message in the UI for now. This feature does not yet interact with the Basalam API but demonstrates how users can communicate with sellers.

## How It Works

The AI agent processes user queries in Persian, extracts relevant parameters (e.g., product type, price range, city, rating), and uses the Basalam API to fetch matching products. It then formats the results into a structured and user-friendly response.

## Chat History Feature

The AI agent supports a **chat history** feature, allowing it to provide context-aware responses by remembering previous interactions in the conversation.

### How It Works

The `chat_history` stores the conversation as a sequence of messages. Each message includes:
- `role`: Specifies whether the message is from the "user" or the "assistant".
- `content`: The text of the message.

This history is passed to the agent with each new query, enabling it to respond based on the context of the entire conversation.

### Example

1. **User Input**:
    ```
    گزینه‌های ارزان قیمت چیست؟
    ```
    **Agent Response**:
    ```
    گزینه‌های ارزان قیمت: محصول A (۱۰ دلار)، محصول B (۱۵ دلار)، محصول C (۲۰ دلار).
    ```

2. **Follow-Up Query**:
    ```
    کدام یکی از پیشنهادات شما ارزان‌تر است؟
    ```
    **Agent Response**:
    ```
    ارزان‌ترین گزینه محصول A است که قیمت آن ۱۰ دلار است.
    ```

In this example, the agent uses the chat history to understand the follow-up question and provide a relevant response.

## Project Structure

```bash
├── app.py               # Streamlit frontend
├── chat.py             # LangChain agent and logic
├── tools/              # Folder containing all tools
│   ├── basalam_search.py    # Tool for calling Basalam API
│   ├── generate_message.py  # Tool for generating seller messages
│   └── intent_detector.py   # Tool for detecting user intent
├── prompts/
│   └── base.txt        # Main system prompt for the assistant
├── requirements.txt    # Python dependencies
├── .env               # API key environment variables (not committed)
└── README.md          # Project documentation
```


## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- A Basalam API key
- An OpenAI or compatible LLM API key

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/m451h/basalamAiAgent.git
    cd basalamAiAgent
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Add your API keys to the `.env` file:
    ```dotenv
    OPENAI_API_KEY=your_openai_key
    OPENAI_API_BASE=https://api.groq.com/openai/v1
    ```

### Running the Application

1. Start the Streamlit app:
    ```bash
    streamlit run app.py
    ```

2. Open the app in your browser at `http://localhost:8501`.



## Deployment

The app can be deployed to platforms like **Render**, **Heroku**, or **Streamlit Cloud**. Update the `.env` file with your production API keys before deployment.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author

Created by **Masih** (m451h).
