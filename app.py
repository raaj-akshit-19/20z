from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
from fpdf import FPDF
import os

app = Flask(__name__)
app.static_folder = 'plans'

# Load workout dataset
try:
    df = pd.read_csv("Workout_Dataset.csv")
    if df.empty:
        raise ValueError("Workout_Dataset.csv is empty.")
except Exception as e:
    print("❌ Failed to load dataset:", e)
    df = pd.DataFrame()

@app.route('/')
def home():
    return "✅ AI Gym Planner API is running."

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json(force=True)

        # Input validation
        username = data.get('username')
        current_weight = data.get('current_weight')
        target_weight = data.get('target_weight')
        days = data.get('days')

        if not all([username, current_weight, target_weight, days]):
            return jsonify({"error": "Missing one or more required fields: username, current_weight, target_weight, days"}), 400

        try:
            current_weight = float(current_weight)
            target_weight = float(target_weight)
            days = int(days)
        except ValueError:
            return jsonify({"error": "Weight and days must be numeric values."}), 400

        if df.empty:
            return jsonify({"error": "Workout dataset not loaded."}), 500

        # Determine goal
        if current_weight > target_weight:
            goal = "reduce"
        elif current_weight < target_weight:
            goal = "increase"
        else:
            goal = "maintain"

        workouts = df[df['Goal'].str.lower() == goal]
        if workouts.empty:
            return jsonify({"error": f"No workouts available for goal: {goal}"}), 500

        sampled = workouts.sample(n=days, replace=True).reset_index(drop=True)
        plan = []

        for i in range(days):
            w = sampled.iloc[i]
            sets_or_time = f"{w['Sets']} minutes" if w['Workout'].lower() == "treadmill jog" else w['Sets']
            plan.append({
                "Day": f"Day {i+1}",
                "Workout": w['Workout'],
                "Muscle": w['Muscle'],
                "Sets": sets_or_time,
                "Steps": 6000 if goal == "maintain" else (7000 if goal == "reduce" else 5000),
                "Calories": 2000 if goal == "maintain" else (1700 if goal == "reduce" else 2300)
            })

        # Generate PDF
        os.makedirs("plans", exist_ok=True)
        filename = f"{username.lower().replace(' ', '_')}_plan.pdf"
        filepath = os.path.join("plans", filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"🏋️ Gym Plan for {username}", ln=True, align='C')
        pdf.ln(10)

        for item in plan:
            pdf.cell(200, 10, txt=f"{item['Day']}:", ln=True)
            pdf.cell(200, 10, txt=f"  Workout: {item['Workout']}", ln=True)
            pdf.cell(200, 10, txt=f"  Muscle: {item['Muscle']}", ln=True)
            pdf.cell(200, 10, txt=f"  Sets/Time: {item['Sets']}", ln=True)
            pdf.cell(200, 10, txt=f"  Steps: {item['Steps']}", ln=True)
            pdf.cell(200, 10, txt=f"  Calories: {item['Calories']} kcal", ln=True)
            pdf.ln(5)

        pdf.output(filepath)

        pdf_url = f"https://gymplanner-api.onrender.com/plans/{filename}"
        return jsonify({"pdf_link": pdf_url})

    except Exception as e:
        print("❌ Unexpected error in /generate-plan:", e)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/plans/<path:filename>', methods=['GET'])
def serve_pdf(filename):
    try:
        return send_from_directory("plans", filename)
    except Exception as e:
        return jsonify({"error": f"Could not fetch PDF: {e}"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
