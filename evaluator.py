# evaluator_service.py
import time
import re
import ollama
from concurrent import futures
import grpc
import evaluator_pb2 as evaluator_pb2
import evaluator_pb2_grpc as evaluator_pb2_grpc

MODELS = ["gemma2:9b",        
    "deepseek-r1:8b",
    "mistral:7b"] 

def parse_response(output, marks):
    score = None
    feedback = output.strip()
    match = re.search(r"(\d+)\s*/\s*" + str(marks), output)
    if match:
        score = match.group(1)
    else:
        match = re.search(r"\b(\d+)\b", output)
        if match:
            score = match.group(1)
    if score is None:
        score = "0"
    return int(score), feedback

class EvaluatorServicer(evaluator_pb2_grpc.EvaluatorServicer):
    def Evaluate(self, request, context):
        question = request.question
        user_answer = request.user_answer
        marks = request.marks
        model = MODELS[0]  

        prompt = f"""
Question: {question}
User Answer: {user_answer}
Marks: {marks}
Task: Give Score (0-{marks}) and Feedback in 1 sentence.
"""
        start_time = time.time()
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        end_time = time.time()
        runtime = round(end_time - start_time, 2)
        output = response["message"]["content"]
        score, feedback = parse_response(output, marks)

        return evaluator_pb2.EvaluateResponse(score=score, time_taken=runtime, feedback=feedback)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    evaluator_pb2_grpc.add_EvaluatorServicer_to_server(EvaluatorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC Evaluator running on port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
