from flask import Flask, render_template, jsonify, request
import requests
import random
import html

app = Flask(__name__)

# Global variable to hold quiz data
quiz_data = []

def fetch_quiz_data():
    """Fetch questions and answers from the OpenTDB API (Film category)."""
    global quiz_data
    try:
        response = requests.get("https://opentdb.com/api.php?amount=5&category=11&type=multiple")
        data = response.json()
        if data["response_code"] == 0:
            quiz_data = [
                {
                    "question": html.unescape(item["question"]),
                    "options": [html.unescape(opt) for opt in item["incorrect_answers"]] + [html.unescape(item["correct_answer"])],
                    "answer": html.unescape(item["correct_answer"]),
                }
                for item in data["results"]
            ]
            for item in quiz_data:
                random.shuffle(item["options"])  # Shuffle options
        else:
            quiz_data = []  # Clear quiz data if fetching fails
    except Exception as e:
        quiz_data = []  # Clear quiz data on error

@app.route('/')
def index():
    """Render the initial quiz page."""
    fetch_quiz_data()
    if quiz_data:
        return render_template('index.html', question=quiz_data[0]["question"], options=quiz_data[0]["options"], current_question=0)
    return "Error loading quiz data!"

@app.route('/quiz_data', methods=['GET'])
def get_quiz_data():
    """Provide quiz data as JSON for frontend use."""
    if quiz_data:
        return jsonify(quiz_data)
    return jsonify({"error": "Quiz data not available"}), 500

@app.route('/next_question', methods=['POST'])
def next_question():
    """Handle moving to the next question and updating the score."""
    global quiz_data
    current_question = int(request.form['current_question'])
    selected_answer = request.form['answer']
    score = int(request.form['score'])

    if selected_answer == quiz_data[current_question]["answer"]:
        score += 1

    current_question += 1
    if current_question < len(quiz_data):
        next_question = quiz_data[current_question]
        return jsonify({
            "question": next_question["question"],
            "options": next_question["options"],
            "current_question": current_question,
            "score": score
        })
    else:
        return jsonify({
            "message": f"You scored {score}/{len(quiz_data)}!",
            "score": score
        })

if __name__ == '__main__':
    app.run(debug=True)
