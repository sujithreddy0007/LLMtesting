from flask import Flask, request, render_template_string
import grpc
import evaluator_pb2 as evaluator_pb2
import evaluator_pb2_grpc as evaluator_pb2_grpc

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>LLM Evaluator</title></head>
<body>
<h1>Answer Evaluator</h1>
<form method="post">
  <label>Question:</label><br>
  <textarea name="question" rows="2" cols="50" required></textarea><br><br>
  <label>User Answer:</label><br>
  <textarea name="user_answer" rows="3" cols="50" required></textarea><br><br>
  <label>Total Marks:</label><br>
  <input type="number" name="marks" required><br><br>
  <input type="submit" value="Evaluate">
</form>

{% if result %}
<h2>Result:</h2>
<b>Score:</b> {{ result.score }} / {{ marks }}<br>
<b>Time Taken:</b> {{ result.time_taken }} seconds<br>
<b>Feedback:</b> {{ result.feedback }}<br>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    marks = None
    if request.method == "POST":
        question = request.form["question"]
        user_answer = request.form["user_answer"]
        marks = int(request.form["marks"])

        # Connect to gRPC server
        channel = grpc.insecure_channel("localhost:50051")
        stub = evaluator_pb2_grpc.EvaluatorStub(channel)
        request_proto = evaluator_pb2.EvaluateRequest(
            question=question,
            user_answer=user_answer,
            marks=marks
        )
        result = stub.Evaluate(request_proto)

    return render_template_string(TEMPLATE, result=result, marks=marks)

if __name__ == "__main__":
    app.run(debug=True)
