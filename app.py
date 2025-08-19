from flask import Flask, request, render_template_string
from backend.evaluator import evaluate_answer  # Import evaluator function

app = Flask(__name__)

# Simple HTML template
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LLM Evaluator</title>
</head>
<body style="font-family: Arial; margin: 30px;">
    <h1>Local LLM Answer Evaluator</h1>

    <form method="post">
        <label>Question:</label><br>
        <textarea name="question" rows="2" cols="80" required></textarea><br><br>

        <label>Correct Answer:</label><br>
        <textarea name="correct_answer" rows="3" cols="80" required></textarea><br><br>

        <label>User Answer:</label><br>
        <textarea name="user_answer" rows="3" cols="80" required></textarea><br><br>

        <label>Total Marks:</label><br>
        <input type="number" name="marks" required><br><br>

        <input type="submit" value="Evaluate">
    </form>

    {% if results %}
        <h2>Evaluation Results:</h2>
        {% for model, output, runtime in results %}
            <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
                <b>Model:</b> {{ model }}<br>
                <pre>{{ output }}</pre>
                <b>Time Taken:</b> {{ runtime }} seconds
            </div>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    if request.method == "POST":
        question = request.form["question"]
        correct_answer = request.form["correct_answer"]
        user_answer = request.form["user_answer"]
        marks = int(request.form["marks"])

        results = evaluate_answer(question, user_answer, correct_answer, marks)

    return render_template_string(TEMPLATE, results=results)


if __name__ == "__main__":
    app.run(debug=True)
