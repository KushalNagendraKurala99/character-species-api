import streamlit as st
import requests

# --- Backend URLs ---
GRAPHQL_URL = "http://127.0.0.1:5000/graphql"
NLP_URL = "http://127.0.0.1:5010/nlp"

# --- Page config ---
st.set_page_config(page_title="Star Wars GraphQL + LLM", layout="wide")
st.title("Star Wars Database Interface")
st.write(
    "Ask questions or perform CRUD operations in **natural language**. "
    "The system will translate them into MongoDB/GraphQL commands."
)

# --- Section 1: Natural Language to MongoDB ---
st.header("Natural Language to MongoDB")
nl_query = st.text_area("Enter your request (e.g., 'Insert a character named Yoda with height 66')")

if st.button("Run NLP Query"):
    if nl_query.strip() == "":
        st.warning("Please enter a query first.")
    else:
        try:
            resp = requests.post(NLP_URL, json={"llm_command": nl_query})
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    st.subheader("✅ NLP Response (JSON)")
                    st.json(data)
                except Exception:
                    st.error("❌ Response was not valid JSON")
                    st.text(resp.text)
            else:
                st.error(f"❌ Server error: {resp.status_code}")
                st.text(resp.text)
        except Exception as e:
            st.error(f"Failed to reach NLP API: {e}")

st.markdown("---")

# --- Section 2: Direct GraphQL Query ---
st.header("  Direct GraphQL Query")
example_query = """
{
  characters(name: "Yoda") {
    id
    name
    height
  }
}
"""
graphql_query = st.text_area("GraphQL query:", value=example_query, height=200)

if st.button("Run GraphQL Query"):
    try:
        resp = requests.post(GRAPHQL_URL, json={"query": graphql_query})
        if resp.status_code == 200:
            try:
                data = resp.json()
                st.subheader("✅ GraphQL Response")
                st.json(data)
            except Exception:
                st.error("❌ Response was not valid JSON")
                st.text(resp.text)
        else:
            st.error(f"❌ GraphQL error: {resp.status_code}")
            st.text(resp.text)
    except Exception as e:
        st.error(f"Failed to reach GraphQL API: {e}")
