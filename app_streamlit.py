import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="🧞 Gym Genie", layout="centered")
st.markdown(
    "<h1 style='text-align: center; color: #00adb5;'>🧞 Gym Genie</h1>", 
    unsafe_allow_html=True
)

with st.form("user_form"):
    username = st.text_input("👤 Enter your name")
    current_weight = st.number_input("⚖️ Current Weight (kg)", min_value=30.0, max_value=200.0)
    target_weight = st.number_input("🎯 Target Weight (kg)", min_value=30.0, max_value=200.0)
    days = st.number_input("📅 Number of Days for Plan", min_value=1, max_value=30)
    submitted = st.form_submit_button("Generate Plan")

if submitted:
    with st.spinner("Generating your plan..."):
        payload = {
            "username": username,
            "current_weight": current_weight,
            "target_weight": target_weight,
            "days": days
        }
        try:
            response = requests.post("https://gymplanner-api.onrender.com/generate-plan", json=payload)
            data = response.json()

            if "plan" in data:
                st.success(f"Here’s your personalized plan, {data['username']} 💪")

                df = pd.DataFrame(data["plan"])
                df.set_index("Day", inplace=True)

                def style_table(df):
                    return df.style.set_table_styles([
                        {'selector': 'th', 'props': [('background-color', '#00adb5'), ('color', 'white'), ('padding', '8px')]},
                        {'selector': 'td', 'props': [('padding', '8px')]},
                    ]).format({
                        "Calories": "{:.0f} kcal",
                        "Steps": "{:.0f} steps"
                    })

                st.write(style_table(df).to_html(), unsafe_allow_html=True)
            else:
                st.error(data.get("error", "Something went wrong."))

        except Exception as e:
            st.error("Server error or invalid response.")
