from flask import Flask, request, jsonify
import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime

app = Flask(__name__)

# Set the folder to serve PDFs
app.static_folder = 'plans'

# Load workout dataset
try:
    df = pd.read_csv("Workout_Dataset.csv")
except Exception as e:
    print("❌ Error loading Workout_Dataset.csv:", e)
    df = pd.DataFrame()

@app.route('/')
def home():
    return "✅ AI Gym Planner API is running."

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json()

        # Input validation
        username = data.get('username')
        current_weight = float(data.get('current_weight'))
        target_weight = float(data.get('target_weight'))
        days = int(data.get('days'))

        if not all([username, current_weight, target_weight, days]):
            return jsonify({"error": "Missing required inputs"}), 400

        # Determine goal
        if current_weight > target_weight:
            goal = "reduce"
        elif current_weight < target_weight:
            goal = "increase"
        else:
            goal = "maintain"

        # Filter workouts based on goal
        workouts = df[df['Goal'].str.lower() == goal].sample(n=days, replace=True).reset_index(drop=True)

        plan = []
        for i in range(days):
            workout = workouts.iloc[i]
            workout_name = workout["Workout"]
            sets_or_time = f"{workout['Sets']} minutes" if workout_name.lower() == "treadmill jog" else workout["Sets"]

            item = {
                "Day": f"Day {i + 1}",
                "Workout": workout_name,
                "Muscle": workout["Muscle"],
                "Sets": sets_or_time,
                "Steps": 6000 if goal == "maintain" else (7000 if goal == "reduce" else 5000),
                "Calories": 2000 if goal == "maintain" else (1700 if goal == "reduce" else 2300)
            }
            plan.append(item)

        # Generate PDF
        os.makedirs("plans", exist_ok=True)
        filename = f"{username.lower().replace(' ', '_')}_plan.pdf"
        filepath = os.path.join("plans", filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"🏋️ Gym & Lifestyle Plan for {username}", ln=True, align='C')
        pdf.ln(10)

        for item in plan:
            pdf.cell(200, 10, txt=f"{item['Day']}:", ln=True)
            pdf.cell(200, 10, txt=f"  Workout: {item['Workout']}", ln=True)
            pdf.cell(200, 10, txt=f"  Muscle Targeted: {item['Muscle']}", ln=True)
            pdf.cell(200, 10, txt=f"  Sets/Time: {item['Sets']}", ln=True)
            pdf.cell(200, 10, txt=f"  Step Goal: {item['Steps']} steps", ln=True)
            pdf.cell(200, 10, txt=f"  Calorie Intake: {item['Calories']} kcal", ln=True)
            pdf.ln(5)

        pdf.output(filepath)

        # Generate link to PDF
        pdf_link = f"https://gymplanner-api.onrender.com/plans/{filename}"
        return jsonify({"pdf_link": pdf_link})

    except Exception as e:
        print("❌ Error in /generate-plan:", e)
        return jsonify({"error": str(e)}), 500

# Serve PDF files from the /plans endpoint
@app.route('/plans/<filename>', methods=['GET'])
def serve_pdf(filename):
    try:
        return app.send_static_file(f"plans/{filename}")
    except Exception as e:
        return jsonify({"error": f"Unable to fetch PDF: {e}"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
