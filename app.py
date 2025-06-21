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

        # Decide goal based on weight
        if current_weight > target_weight:
            goal = "reduce"
            filtered_df = df[df["Type"].str.lower() == "cardio"]
        elif current_weight < target_weight:
            goal = "increase"
            filtered_df = df[df["Type"].str.lower() == "strength"]
        else:
            goal = "maintain"
            filtered_df = df  # use all types

        if filtered_df.empty:
            return jsonify({"error": f"No workouts available for goal: {goal}"}), 500

        sampled = filtered_df.sample(n=days, replace=True).reset_index(drop=True)

        plan = []
        for i in range(days):
            w = sampled.iloc[i]
            plan.append({
                "Day": f"Day {i+1}",
                "Workout": w['Workout Name'],
                "Muscle": w['Muscle'],
                "Sets/Time": w['Reps/Time'],
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
