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

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "🏋️ Gym & Lifestyle Plan", ln=True, align="C")
        self.ln(5)

    def table_header(self):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(200, 220, 255)
        self.cell(15, 10, "Day", 1, 0, 'C', 1)
        self.cell(45, 10, "Workout", 1, 0, 'C', 1)
        self.cell(30, 10, "Muscle", 1, 0, 'C', 1)
        self.cell(40, 10, "Sets/Time", 1, 0, 'C', 1)
        self.cell(30, 10, "Steps", 1, 0, 'C', 1)
        self.cell(30, 10, "Calories", 1, 1, 'C', 1)

    def table_row(self, day, workout, muscle, reps_time, steps, cal):
        self.set_font("Arial", "", 11)
        self.cell(15, 10, str(day), 1, 0, 'C')
        self.cell(45, 10, workout, 1, 0, 'C')
        self.cell(30, 10, muscle, 1, 0, 'C')
        self.cell(40, 10, reps_time, 1, 0, 'C')
        self.cell(30, 10, str(steps), 1, 0, 'C')
        self.cell(30, 10, str(cal), 1, 1, 'C')

@app.route('/')
def home():
    return "✅ AI Gym Planner API is running."

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json(force=True)

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

        sampled = df.sample(n=days, replace=True).reset_index(drop=True)
        plan = []

        for i in range(days):
            w = sampled.iloc[i]
            plan.append({
                "Day": f"{i + 1}",
                "Workout": w["Workout Name"],
                "Muscle": w["Muscle"],
                "Sets": w["Reps/Time"],
                "Steps": 6000 if goal == "maintain" else (7000 if goal == "reduce" else 5000),
                "Calories": 2000 if goal == "maintain" else (1700 if goal == "reduce" else 2300)
            })

        # Create PDF with table
        os.makedirs("plans", exist_ok=True)
        filename = f"{username.lower().replace(' ', '_')}_plan.pdf"
        filepath = os.path.join("plans", filename)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Name: {username}", ln=True)
        pdf.cell(0, 10, f"Goal: {goal.title()} weight ({current_weight}kg → {target_weight}kg)", ln=True)
        pdf.ln(5)
        pdf.table_header()

        for item in plan:
            pdf.table_row(item["Day"], item["Workout"], item["Muscle"], item["Sets"], item["Steps"], item["Calories"])

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
