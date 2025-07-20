import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
import matplotlib.pyplot as plt

# --- Groq API Client Initialization ---
client = Groq(api_key="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")

# --- Streamlit UI Config ---
st.set_page_config(page_title="MG Knowledge + AI Dashboard", layout="centered")
st.title("🤖 MG Company Knowledge Chatbot + 📊 AI Dashboard Generator")

# --- Section 1: MG Apparel Chatbot ---
st.header("🧠 MG Apparel Knowledge Chatbot")
st.markdown("Upload your knowledge base (CSV) and ask questions.")

# --- Upload Knowledge Base ---
kb_file = st.file_uploader("📁 Upload Knowledge Base (CSV)", type=["csv"])
MG_KNOWLEDGE_BASE = ""

if kb_file:
    try:
        kb_df = pd.read_csv(kb_file)
        st.success("✅ Knowledge base uploaded successfully!")

        with st.expander("📂 Preview Knowledge Base"):
            st.dataframe(kb_df.head())

        if 'Answer' in kb_df.columns:
            MG_KNOWLEDGE_BASE = "\n".join(kb_df['Answer'].astype(str))
        elif 'Content' in kb_df.columns:
            MG_KNOWLEDGE_BASE = "\n".join(kb_df['Content'].astype(str))
        else:
            MG_KNOWLEDGE_BASE = "\n".join(kb_df.astype(str).agg(" ".join, axis=1))
    except Exception as e:
        st.error(f"❌ Failed to read uploaded knowledge base. Error: {e}")

# --- Ask Question Section ---
if MG_KNOWLEDGE_BASE:
    st.subheader("💬 Ask a Question")
    user_input = st.text_input("Your question about MG Apparel:")

    if st.button("Ask"):
        if user_input.strip() == "":
            st.error("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                prompt = f"""
You are an assistant for MG Apparel. ONLY use the MG company information provided below to answer the user's question.
If the answer is not present in the knowledge base, respond with:
"I can't answer that based on the MG company knowledge provided."

MG Company Knowledge Base:
{MG_KNOWLEDGE_BASE}

User Question:
{user_input}
"""

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=700,
                )

                answer = response.choices[0].message.content.strip()
                st.markdown("### 🤖 MG Bot Response")
                st.markdown(answer)

# --- Section 2: AI Dashboard Generator ---
st.markdown("---")
st.header("📊 AI Dashboard Generator")
st.markdown("Upload a CSV and describe the dashboard you'd like.")

uploaded_file = st.file_uploader("📁 Upload your CSV file", type=["csv"], key="dashboard_csv")

if uploaded_file:
    try:
        data = pd.read_csv(uploaded_file)
        st.success("✅ CSV uploaded and data loaded!")

        with st.expander("📂 Preview Uploaded Data"):
            st.dataframe(data.head())

        user_dashboard_request = st.text_area("🧾 Describe your dashboard (e.g., 'Bar chart of sales by region, line chart of monthly trends')")

        if st.button("🚀 Build Dashboard"):
            if user_dashboard_request.strip() == "":
                st.warning("Please enter a dashboard request.")
            else:
                with st.spinner("🤖 Generating your dashboard..."):
                    ai_prompt = f"""
You are a Python data visualization assistant.

The user uploaded a dataset (loaded as a DataFrame called `data`) and gave a request for a dashboard.

ONLY return clean, executable Python code using Plotly Express and Streamlit. Do NOT include explanations, markdown, comments, or code fences. DO NOT write imports or data loading.

Your output MUST start with `fig =` or `chart =` and use `st.plotly_chart()` to display the charts.

User Request:
{user_dashboard_request}

Dataset Sample:
{data.head(5).to_csv(index=False)}
"""

                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": ai_prompt}],
                        temperature=0.2,
                        max_tokens=1000,
                    )

                    generated_code = response.choices[0].message.content.strip()
                    clean_code = generated_code.replace("```python", "").replace("```", "").strip()

                    try:
                        exec_globals = {
                            "data": data,
                            "st": st,
                            "px": px,
                            "plt": plt
                        }
                        exec(clean_code, exec_globals)
                        st.success("✅ Dashboard created successfully!")
                    except Exception as e:
                        st.error(f"⚠️ Error while creating dashboard: {e}")
    except Exception as e:
        st.error(f"❌ Error reading uploaded CSV: {e}")
