# Nexus Lab AI Assistant

A Streamlit chat assistant powered by Groq. It can use PDF files in the `research/` folder as reference material, optionally search the web with Tavily, and retain conversation context while the current Streamlit session is active.

## Features

- Conversational chat with streamed responses and session-based chat history.
- PDF question answering: PDFs in `research/` are loaded, split into text chunks, embedded with `sentence-transformers/all-MiniLM-L6-v2`, and indexed with FAISS. The top three matching chunks are sent to the model as context.
- Optional web search using Tavily. Enable **Enable Tavily Web Search** in the sidebar and provide a Tavily API key.
- Sidebar controls for Groq model, temperature, and maximum response tokens.
- **Clear Chat** button to reset the conversation.
- Custom dark theme and Nexus Lab footer.

## Requirements

- Python 3.9 or newer
- A [Groq API key](https://console.groq.com/keys)
- Optional: a [Tavily API key](https://app.tavily.com/) to use web search

## Installation

Create and activate a virtual environment in the project directory:

```bash
python -m venv .venv
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install -r requirement.txt
```

## Add research PDFs

Place PDF files directly inside the `research/` folder. The app loads and indexes them when needed. If the folder contains no PDFs, the assistant still works as a general Groq chatbot; PDF search context is simply unavailable. The first embedding run may download the Hugging Face sentence-transformer model.

## Run

From the project directory, start the app:

```bash
streamlit run main.py
```

Open the local URL shown in the terminal. Enter your Groq API key in the sidebar and ask a question in the chat box. To include web results, also enter a Tavily API key and turn on web search.

The model choices currently configured in the app are:

- `openai/gpt-oss-120b`
- `openai/gpt-oss-20b`
- `qwen/qwen3.8-27b`

## Configuration

The app optionally reads `LANGCHAIN_API_KEY` from a `.env` file for LangSmith integration. Keep API keys private and do not commit `.env` to version control. Groq and Tavily keys can be entered in the sidebar when the app runs.

## Project structure

```text
.
├── main.py                 # Streamlit UI, Groq chat, PDF retrieval, optional web search
├── style.py                # Theme and footer rendering
├── footer.py               # Legacy footer renderer
├── requirement.txt         # Python dependencies
├── research/               # Add PDF documents here
└── .streamlit/config.toml  # Streamlit theme and server settings
```
