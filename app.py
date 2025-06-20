from flask import Flask, request, jsonify
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

app = Flask(__name__)

@app.route("/generate_plan", methods=["POST"])
def generate_plan():
    data = request.json
    username = data['username']
    current_weight = float(data['current_weight'])
    target_weight = float(data['target_weight'])
    num_days = int(data['num_days'])

    with open("Watsonx_AI_Weight_Plan_With_PDF.ipynb") as f:
        nb = nbformat.read(f, as_version=4)

    code = f'''
username = "{username}"
current_weight = {current_weight}
target_weight = {target_weight}
num_days = {num_days}
    '''

    nb.cells.insert(2, nbformat.v4.new_code_cell(code))
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    ep.preprocess(nb, {'metadata': {'path': './'}})

    output_file = f"{username.lower().strip()}.pdf"
    return jsonify({"pdf_url": f"https://your-storage-or-host/{output_file}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
