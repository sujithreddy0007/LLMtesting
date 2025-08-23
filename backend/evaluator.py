import ollama
import csv
import os
import time
import re
from .models import MODELS  # Relative import for models

# Ensure data folder exists
RESULTS_FOLDER = os.path.join("..", "data")
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

RESULTS_FILE = os.path.join(RESULTS_FOLDER, "results.csv")

# Ensure results.csv exists
if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "User Answer", "Model", "Score", "Feedback", "Time Taken (s)"])


def parse_response(output, marks):
    """Extract score and feedback from model output."""
    score = None
    feedback = output.strip()

    # Try to extract score (e.g., "Score: 3/5" or "3/5")
    match = re.search(r"(\d+)\s*/\s*" + str(marks), output)
    if match:
        score = match.group(1)
    else:
        # fallback: find standalone number
        match = re.search(r"\b(\d+)\b", output)
        if match:
            score = match.group(1)

    if score is None:
        score = "0"  # default if model didn't give a score

    return score, feedback


def evaluate_answer(question, user_answer, correct_answer, marks):
    """Send question, user answer, and correct answer to each model for evaluation."""
    results = []
    for model in MODELS:
        prompt = f"""
        You are an evaluator.
        Question: {question}
        Correct Answer: {correct_answer}
        User Answer: {user_answer}
        Marks: {marks}

        Task: Compare user answer with correct answer and give:
        - Score (0 to {marks})
        - Feedback in 2 sentences
        """

        start_time = time.time()
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        end_time = time.time()

        runtime = round(end_time - start_time, 2)
        output = response["message"]["content"]

        # Parse score + feedback
        score, feedback = parse_response(output, marks)

        results.append((model, score, feedback, runtime))

        # Save results into CSV
        with open(RESULTS_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([question, user_answer, model, score, feedback, runtime])

    return results
