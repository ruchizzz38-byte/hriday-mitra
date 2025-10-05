# app.py
import streamlit as st
import json
from pathlib import Path
from rapidfuzz import process, fuzz

# --- CONFIGURATION ---
st.set_page_config(page_title="Hriday Mitra", layout="centered")
DATA_FILE = Path("faqs.json")
SIMILARITY_THRESHOLD = 70  # A value from 0-100. Higher means more strict matching.

# --- DATA LOADING ---
def load_faqs():
    """Loads FAQs from the JSON file. Returns an empty list if file not found or invalid."""
    if not DATA_FILE.exists():
        st.error(f"Error: The data file '{DATA_FILE}' was not found. Please create it.")
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        st.error(f"Error: Could not read or parse '{DATA_FILE}'. Make sure it's a valid JSON file.")
        return []

def save_faqs(faqs):
    """Saves the list of FAQs to the JSON file."""
    try:
        DATA_FILE.write_text(json.dumps(faqs, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        st.error(f"Failed to save FAQs: {e}")

# --- CORE LOGIC ---
def find_best_match(query, faqs):
    """Finds the best matching question from the FAQs using fuzzy string matching."""
    if not faqs:
        return None, 0

    questions = [faq["question"] for faq in faqs]
    # process.extractOne returns the best match: (matched_question, score, index)
    best_match = process.extractOne(query, questions, scorer=fuzz.WRatio)

    if best_match and best_match[1] >= SIMILARITY_THRESHOLD:
        # If score is above threshold, return the corresponding answer and score
        best_question, score, index = best_match
        return faqs[index]["answer"], score
    return None, best_match[1] if best_match else 0

# --- UI & APP LOGIC ---
faqs = load_faqs()

st.title("🩺 Hriday Mitra 🫀🫶🏻")
st.markdown("**Disclaimer:** Namaste!🙏 I am your health assistant for information on high blood pressure (Hypertension), based on Indian health guidelines. I am not a doctor. How can I help you today?")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about hypertension or CVD..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Find and display bot response
    with st.chat_message("assistant"):
        answer, score = find_best_match(prompt, faqs)
        if answer:
            response = f"{answer}\n\n*(Match score: {int(score)}%)*"
            st.markdown(response)
        else:
            response = "I couldn't find a confident answer in my knowledge base. Please try rephrasing your question or consult a healthcare professional for specific advice."
            st.warning(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- ADMIN SECTION (in sidebar) ---
with st.sidebar:
    st.header("Admin Panel")
    if st.checkbox("Add or Edit FAQs"):
        st.subheader("Current FAQs")
        for i, faq in enumerate(faqs):
            with st.expander(f"{i+1}. {faq['question']}"):
                st.text_area("Answer", value=faq['answer'], key=f"ans_{i}", height=150)
                if st.button("Delete this FAQ", key=f"del_{i}"):
                    faqs.pop(i)
                    save_faqs(faqs)
                    st.success("FAQ deleted. Please refresh the page.")
                    st.stop()

        st.subheader("Add New FAQ")
        new_q = st.text_input("New Question")
        new_a = st.text_area("New Answer")
        if st.button("Add FAQ"):
            if new_q.strip() and new_a.strip():
                faqs.append({"question": new_q.strip(), "answer": new_a.strip()})
                save_faqs(faqs)
                st.success("FAQ added successfully. Please refresh the page to see changes.")
            else:
                st.error("Please provide both a question and an answer.")