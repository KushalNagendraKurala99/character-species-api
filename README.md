# character-species-api


## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your own MongoDB connection string:
   ```bash
   cp .env.example .env
   ```

## Project files

- `app_graphql.py` — GraphQL API (Ariadne + Flask)
- `app_streamlit.py` — Streamlit frontend
- `db.py` — MongoDB connection setup
- `nlp_api.py` — NLP-related API logic
- `normalize_arrays.py` — Data normalization utilities
- `test_db.py` — DB connection test script
- `INSTRUCTIONS/` — Original assignment instructions (PDF)

## Running

```bash
# GraphQL API
python app_graphql.py

# Streamlit app
streamlit run app_streamlit.py
```
