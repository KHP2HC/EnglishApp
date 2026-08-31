import streamlit as st
import requests
import json
import os

API_PORT = os.environ.get("API_PORT", "8000")
API_URL = f"http://localhost:{API_PORT}/api"

st.set_page_config(page_title="EnglishCoachPro", layout="wide")

st.sidebar.title("EnglishCoachPro")
page = st.sidebar.radio("Navigate", ["Dashboard", "Vocabulary (SRS)", "Reading Practice", "Listening Practice"])

def dashboard_page():
    st.title("Dashboard")
    st.write("Welcome to your English Coach Pro web dashboard!")
    st.info("Select a module from the sidebar to begin studying.")

def vocabulary_page():
    st.title("Vocabulary (Spaced Repetition)")
    st.write("Review your vocabulary flashcards here.")
    st.warning("Ensure the backend API is running to fetch cards.")
    
    # Example hardcoded UI representation
    st.markdown("### Example Flashcard")
    st.markdown("**Word:** `Obfuscate`")
    if st.button("Show Answer"):
        st.markdown("**Meaning:** To make something unclear or difficult to understand.")
        
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Again (0)"):
            st.success("Rated: Again")
        if col2.button("Hard (2)"):
            st.success("Rated: Hard")
        if col3.button("Good (3)"):
            st.success("Rated: Good")
        if col4.button("Easy (5)"):
            st.success("Rated: Easy")

def reading_page():
    st.title("Reading Practice")
    st.write("IELTS Academic Reading Module")
    
    try:
        response = requests.get(f"{API_URL}/reading/tests")
        if response.status_code == 200:
            tests = response.json()
            if not tests:
                st.info("No reading tests available in the seed file.")
                return
            
            test_options = {t["title"]: t["id"] for t in tests}
            selected_test = st.selectbox("Select a Practice Test", list(test_options.keys()))
            
            if st.button("Start Test"):
                st.session_state["active_test_id"] = test_options[selected_test]
                
        if "active_test_id" in st.session_state:
            test_id = st.session_state["active_test_id"]
            st.write(f"Loading test ID: {test_id}...")
            
            test_resp = requests.get(f"{API_URL}/reading/test/{test_id}")
            if test_resp.status_code == 200:
                test_data = test_resp.json()
                st.subheader(test_data.get("title", "Practice Test"))
                
                passages = test_data.get("passages", [])
                
                tabs = st.tabs([f"Passage {i+1}" for i in range(len(passages))])
                user_answers = {}
                
                for i, passage in enumerate(passages):
                    with tabs[i]:
                        col1, col2 = st.columns([6, 4])
                        with col1:
                            st.markdown(passage.get("text", "No text provided."))
                        with col2:
                            st.write("Questions:")
                            for q in passage.get("questions", []):
                                user_answers[q["id"]] = st.text_input(
                                    f"Q{q['number']}: {q.get('text', '')}", 
                                    key=f"q_{q['id']}"
                                )
                
                if st.button("Submit Answers"):
                    st.write("Grading...")
                    grade_resp = requests.post(
                        f"{API_URL}/reading/test/{test_id}/grade", 
                        json={"answers": user_answers}
                    )
                    if grade_resp.status_code == 200:
                        st.json(grade_resp.json())
                    else:
                        st.error("Failed to grade test.")
                        
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        st.info("Please make sure you have started the backend API server.")

def listening_page():
    st.title("Listening Practice")
    st.write("Coming soon! This module will integrate with text-to-speech for interactive dictation.")

if page == "Dashboard":
    dashboard_page()
elif page == "Vocabulary (SRS)":
    vocabulary_page()
elif page == "Reading Practice":
    reading_page()
elif page == "Listening Practice":
    listening_page()