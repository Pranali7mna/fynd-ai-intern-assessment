import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# YOUR GEMINI KEY IS ALREADY HERE
genai.configure(api_key="AIzaSyDVO4jAa6__ugdc1Dc9emwnd2NtJMJIu90")

# UPDATED TO CURRENT FREE MODEL (December 2025)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Fynd Feedback System", layout="wide")
DATA_FILE = "reviews.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=["timestamp", "rating", "review", "ai_response", "ai_summary", "ai_actions"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

tab1, tab2 = st.tabs(["User Feedback", "Admin Dashboard"])

with tab1:
    st.title("Customer Feedback")
    st.write("We value your opinion!")

    rating = st.selectbox("Select rating (1-5 stars)", [1, 2, 3, 4, 5], index=4)
    review = st.text_area("Write your review", height=150)

    if st.button("Submit Feedback", type="primary"):
        if review.strip():
            with st.spinner("Generating response..."):
                # AI response (free Gemini call)
                resp = model.generate_content(f"Reply politely and professionally to this {rating}-star review: {review}").text

                # AI summary
                summary = model.generate_content(f"Summarize this review in one sentence: {review}").text

                # AI actions
                actions = model.generate_content(f"Suggest 1-2 concrete actions based on this review: {review}").text

            # Save data
            new_row = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "rating": rating,
                "review": review,
                "ai_response": resp,
                "ai_summary": summary,
                "ai_actions": actions
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)

            st.success("Thank you for your feedback!")
            st.balloons()
            st.write("**Our response:**")
            st.write(resp)
        else:
            st.error("Please write a review")

with tab2:
    st.title("Admin Dashboard")
    if df.empty:
        st.info("No feedback submitted yet")
    else:
        st.dataframe(df, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Total Reviews", len(df))
        col2.metric("Average Rating", f"{df['rating'].mean():.2f}")
        st.bar_chart(df["rating"].value_counts().sort_index())
        st.subheader("Latest Reviews")
        st.write(df[["timestamp", "rating", "review", "ai_summary", "ai_actions"]].tail(10))