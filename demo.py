import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Check API key
if not api_key:
    st.error("❌ GEMINI_API_KEY not found in environment variables.")
    st.stop()

# Configure Google Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Clean and preprocess text
def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text("text")
    return clean_text(text)

# Generate an answer using Gemini
def generate_answer(content, query):
    prompt = f"""
    You are a helpful assistant. Using the following content from a PDF:

    {content}

    Please answer the following question:
    {query}

    Provide a clear, concise answer.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error generating answer: {e}"

# Streamlit UI
st.set_page_config(page_title="PDF Q&A Chatbot")
st.title("📄🔍 Ask Questions About Your PDF")

uploaded_pdf = st.file_uploader("📤 Upload a PDF file", type="pdf")

if 'pdf_content' not in st.session_state:
    st.session_state['pdf_content'] = ""

if uploaded_pdf:
    st.session_state['pdf_content'] = extract_text_from_pdf(uploaded_pdf)
    st.success("✅ PDF loaded and text extracted!")

user_query = st.text_input("❓ Enter your question about the PDF")

if st.button("💬 Get Answer") and st.session_state['pdf_content']:
    content = st.session_state['pdf_content']
    answer = generate_answer(content, user_query)
    st.subheader("📘 Answer:")
    st.write(answer)
