
import streamlit as st
import requests

st.set_page_config(page_title="AI Gym & Diet Planner", page_icon="🏋️")

st.title("🏋️ AI Gym & Diet Planner")
st.markdown("Get your personalized workout and nutrition plan based on your goal.")

# Input fields
username = st.text_input("Enter your name")
current_weight = st.number_input("Current Weight (kg)", min_value=20, max_value=200, step=1)
target_weight = st.number_input("Target Weight (kg)", min_value=20, max_value=200, step=1)
days = st.number_input("Number of Days to Achieve Goal", min_value=1, max_value=365, step=1)

# Submit button
if st.button("Generate Plan"):
    if username and current_weight and target_weight and days:
        with st.spinner("Generating your plan..."):
            try:
                response = requests.post(
                    "https://gymplanner-api.onrender.com/generate-plan",
                    json={
                        "username": username,
                        "current_weight": current_weight,
                        "target_weight": target_weight,
                        "days": days
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success("Plan generated successfully! 🎉")
                    st.markdown(f"📄 [Download your plan here]({data['pdf_link']})")
                else:
                    st.error("Something went wrong. Please check your inputs or try again later.")
            except Exception as e:
                st.error(f"Request failed: {e}")
    else:
        st.warning("Please fill in all fields before generating the plan.")
