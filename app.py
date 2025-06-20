from flask import Flask, request, jsonify
import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime

app = Flask(__name__)

# Load workout dataset
df = pd.read_csv("Workout_Dataset.csv")
@app.route('/')
def home():
    return "AI Gym Planner API is running"

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json()
        username = data.get('username')
        current_weight = float(data.get('current_weight'))
        target_weight = float(data.get('target_weight'))
        days = int(data.get('days'))

        if not all([username, current_weight, target_weight, days]):
            return jsonify({"error": "Missing input values"}), 400

        # Determine goal
        if current_weight > target_weight:
            goal = "reduce"
        elif current_weight < target_weight:
            goal = "increase"
        else:
            goal = "maintain"

        # Filter workouts for even distribution
        workouts = df[df['Goal'].str.lower() == goal].sample(n=days, replace=True).reset_index(drop=True)

        plan = []
        for i in range(days):
            workout = workouts.iloc[i]
            item = {
                "Day": f"Day {i + 1}",
                "Workout": workout["Workout"],
                "Muscle": workout["Muscle"],
                "Sets": workout["Sets"] if workout["Workout"].lower() != "treadmill jog" else f"{workout['Sets']} minutes",
                "Steps": 6000 if goal == "maintain" else (7000 if goal == "reduce" else 5000),
                "Calories": 2000 if goal == "maintain" else (1700 if goal == "reduce" else 2300)
            }
            plan.append(item)

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Gym Plan for {username}", ln=True, align='C')
        pdf.ln(5)

        for item in plan:
            pdf.cell(200, 10, txt=f"{item['Day']}:", ln=True)
            pdf.cell(200, 10, txt=f"  Workout: {item['Workout']}", ln=True)
            pdf.cell(200, 10, txt=f"  Muscle Targeted: {item['Muscle']}", ln=True)
            pdf.cell(200, 10, txt=f"  Sets/Time: {item['Sets']}", ln=True)
            pdf.cell(200, 10, txt=f"  Steps: {item['Steps']} steps", ln=True)
            pdf.cell(200, 10, txt=f"  Calorie Intake: {item['Calories']} kcal", ln=True)
            pdf.ln(5)

        filename = f"{username.lower().replace(' ', '_')}_plan.pdf"
        filepath = os.path.join("plans", filename)
        os.makedirs("plans", exist_ok=True)
        pdf.output(filepath)

        # Generate public link (adjust if you're using S3, etc.)
        pdf_link = f"https://gymplanner-api.onrender.com/plans/{filename}"
        return jsonify({"pdf_link": pdf_link})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

# Serve PDF statically
@app.route('/plans/<filename>', methods=['GET'])
def serve_pdf(filename):
    return app.send_static_file(f"plans/{filename}")

# To serve plans from 'plans' folder as static
app.static_folder = 'plans'

if __name__ == '__main__':
    app.run(debug=True)
