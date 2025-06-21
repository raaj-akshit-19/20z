from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
from fpdf import FPDF
import os

app = Flask(__name__)
app.static_folder = 'plans'

# Load the dataset
try:
    df = pd.read_csv("Workout_Dataset.csv")
except Exception as e:
    print("❌ Could not load dataset:", e)
    df = pd.DataFrame()

@app.route('/')
def home():
    return "✅ AI Gym Planner API is running."

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json(force=True)

        username = data.get('username')
        current_weight = float(data.get('current_weight'))
        target_weight = float(data.get('target_weight'))
        days = int(data.get('days'))

        if not all([username, current_weight, target_weight, days]):
            return jsonify({"error": "Missing input values"}), 400

        if current_weight > target_weight:
            goal = "reduce"
        elif current_weight < target_weight:
            goal = "increase"
        else:
            goal = "maintain"

        if df.empty:
            return jsonify({"error": "Dataset not loaded"}), 500

        workouts = df.sample(n=days, replace=True).reset_index(drop=True)

        plan = []
        for i in range(days):
            w = workouts.iloc[i]
            plan.append([
                f"Day {i+1}",
                w["Workout Name"],
                w["Muscle"],
                w["Reps/Time"],
                "6000" if goal == "maintain" else ("7000" if goal == "reduce" else "5000"),
                "2000" if goal == "maintain" else ("1700" if goal == "reduce" else "2300")
            ])

        os.makedirs("plans", exist_ok=True)
        filename = f"{username.lower().replace(' ', '_')}_plan.pdf"
        filepath = os.path.join("plans", filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, f"Gym & Lifestyle Plan for {username}", ln=True, align='C')
        pdf.ln(10)

        # Table Header
        pdf.set_font("Arial", 'B', 12)
        headers = ["Day", "Workout", "Muscle", "Reps/Time", "Steps", "Calories"]
        col_widths = [20, 50, 30, 40, 25, 25]
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 10, h, 1, 0, 'C')
        pdf.ln()

        # Table Rows
        pdf.set_font("Arial", size=11)
        for row in plan:
            for i, val in enumerate(row):
                pdf.cell(col_widths[i], 10, str(val), 1, 0, 'C')
            pdf.ln()

        pdf.output(filepath)

        return jsonify({
            "pdf_link": f"https://gymplanner-api.onrender.com/plans/{filename}"
        })

    except Exception as e:
        print("❌ Error generating plan:", e)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/plans/<path:filename>')
def serve_pdf(filename):
    return send_from_directory("plans", filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
