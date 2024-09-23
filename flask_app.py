from flask import Flask, request, jsonify
import openai
import os
import uuid

app = Flask(__name__)

os.environ['OPENAI_API_KEY'] = 'sk-proj-9zsyUVMHm2AKSedGKrydT3BlbkFJO9NEgTuWPbUn999fjZHl'
os.environ['ASSISTANT_ID'] = 'asst_d0EL2uqJr4G7t3ig2fLRrOxl'

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')
assistant_id = os.getenv('ASSISTANT_ID')
ASSISTANT_ID =assistant_id
# Store threads in-memory (consider using a persistent store for production)
threads = {}

def create_thread():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": "", "assistant_id": ASSISTANT_ID}
        ]
    )
    thread_id = str(uuid.uuid4())
    threads[thread_id] = [{"role": "system", "content": "You are a helpful assistant."}]
    return thread_id

def send_message(thread_id, role, content):
    threads[thread_id].append({"role": role, "content": content, "assistant_id": ASSISTANT_ID})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=threads[thread_id]
    )
    reply = response['choices'][0]['message']['content']
    threads[thread_id].append({"role": "assistant", "content": reply, "assistant_id": ASSISTANT_ID})
    return reply

@app.route('/mcqs', methods=['GET'])
def get_mcqs():
    topic = request.args.get('topic')
    number = int(request.args.get('number', 1))

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    # Call the function to get the MCQs
    try:
        mcqs = generate_mcqs(topic, number)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(mcqs)

@app.route('/rephrase', methods=['POST'])
def rephrase_question():
    data = request.get_json()
    question = data.get('question')
    number = int(data.get('number', 1))

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Call the function to rephrase the question and get MCQs
    try:
        rephrased_mcqs = rephrase_and_generate_mcqs(question, number)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(rephrased_mcqs)

def generate_mcqs(topic, number):
    thread_id = create_thread()
    user_message = f"Generate {number} MCQs for the topic: {topic}."
    mcqs_content = send_message(thread_id, "user", user_message)
    return parse_mcqs(mcqs_content, number)

def rephrase_and_generate_mcqs(question, number):
    thread_id = create_thread()
    user_message = f"Rephrase the following question and generate {number} MCQs: {question}"
    rephrased_content = send_message(thread_id, "user", user_message)
    return parse_mcqs(rephrased_content, number)

def parse_mcqs(mcqs_content, number):
    mcqs = mcqs_content.strip().split('\n\n')  # Assume each MCQ block is separated by double newlines
    parsed_mcqs = []

    for mcq in mcqs[:number]:
        lines = mcq.strip().split('\n')
        question = lines[0]
        options = lines[1:]
        if len(options) < 4:
            continue  # Skip MCQs with less than 4 options
        parsed_mcqs.append({
            "question": question,
            "options": options[:4]  # Only take the first four options
        })

    return parsed_mcqs

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
