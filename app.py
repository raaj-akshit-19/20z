from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

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

        username = data.get('username')
        current_weight = data.get('current_weight')
        target_weight = data.get('target_weight')
        days = data.get('days')

        if not all([username, current_weight, target_weight, days]):
            return jsonify({"error": "Missing required fields."}), 400

        current_weight = float(current_weight)
        target_weight = float(target_weight)
        days = int(days)

        if df.empty:
            return jsonify({"error": "Workout dataset not loaded."}), 500

        goal = "reduce" if current_weight > target_weight else "increase" if current_weight < target_weight else "maintain"
        workouts = df[df['Goal'].str.lower() == goal]

        if workouts.empty:
            return jsonify({"error": f"No workouts available for goal: {goal}"}), 500

        sampled = workouts.sample(n=days, replace=True).reset_index(drop=True)

        plan = []
        for i in range(days):
            w = sampled.iloc[i]
            plan.append({
                "Day": f"Day {i+1}",
                "Workout": w['Workout'],
                "Muscle": w['Muscle'],
                "Sets/Time": w['Sets'],
                "Steps": 6000 if goal == "maintain" else (7000 if goal == "reduce" else 5000),
                "Calories": 2000 if goal == "maintain" else (1700 if goal == "reduce" else 2300)
            })

        return jsonify({"username": username, "plan": plan})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
