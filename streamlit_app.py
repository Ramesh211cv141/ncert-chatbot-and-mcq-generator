import streamlit as st
import openai
import requests

# Initialize OpenAI with your API key
openai.api_key = 'sk-proj-9zsyUVMHm2AKSedGKrydT3BlbkFJO9NEgTuWPbUn999fjZHl'

# Define your assistant ID
assistant_id = 'asst_d0EL2uqJr4G7t3ig2fLRrOxl'

# Initialize session state variables
if 'mcq' not in st.session_state:
    st.session_state.mcq = None
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'correct_count' not in st.session_state:
    st.session_state.correct_count = 0
if 'correct_answer' not in st.session_state:
    st.session_state.correct_answer = ""
if 'options' not in st.session_state:
    st.session_state.options = []

def generate_mcq_from_ncert(topic):
    """
    Generate an MCQ based on the NCERT text and a specified topic using the assistant ID.
    """
    prompt = f"Generate a multiple-choice question with exactly four options on the topic '{topic}' based on NCERT text using the assistant ID {assistant_id}."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a knowledgeable assistant with ID {assistant_id} proficient in NCERT content."},
            {"role": "user", "content": prompt}
        ]
    )
    mcq_content = response['choices'][0]['message']['content']
    # Parsing the MCQ content to extract the question, options, and correct answer
    st.session_state.mcq, st.session_state.correct_answer, st.session_state.options = parse_mcq_content(mcq_content)

def parse_mcq_content(mcq_content):
    """
    Parse the generated MCQ content to extract the question, options, and correct answer.
    """
    lines = mcq_content.strip().split('\n')
    question = lines[0]
    options = lines[1:5]  # Ensure we only take the first 4 options
    correct_answer_line = lines[-1]
    # Assume the last line is in the format: Correct: Option A
    correct_answer = correct_answer_line.split(': ')[1]
    return question, correct_answer, options

def get_explanation_from_ncert(concept):
    """
    Fetch a brief explanation from the NCERT text for a given concept.
    """
    prompt = f"Provide a brief explanation on {concept} from the NCERT text using assistant ID {assistant_id}."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a knowledgeable assistant with ID {assistant_id} proficient in NCERT content."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def evaluate_answer(user_answer, correct_answer):
    """
    Evaluate the user's answer and provide feedback.
    """
    if user_answer == correct_answer:
        st.session_state.feedback = "Correct! Well done."
        st.session_state.correct_count += 1
        st.session_state.explanation = ""  # No explanation needed for correct answer
    else:
        st.session_state.feedback = f"Wrong. The correct answer is {correct_answer}."
        st.session_state.explanation = get_explanation_from_ncert(correct_answer)

# Streamlit UI
st.title("NCERT Chatbot & MCQ Generator")

st.write("### Ask a question based on NCERT text:")
user_query = st.text_input("Enter your query:")
if user_query:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a knowledgeable assistant with ID {assistant_id} proficient in NCERT content."},
            {"role": "user", "content": user_query}
        ]
    )
    st.write("**Answer:** ", response['choices'][0]['message']['content'])

st.write("### Generate a Multiple-Choice Question (MCQ):")
topic = st.text_input("Enter a topic or subtopic for the MCQ:")
if st.button("Generate MCQ"):
    if topic.strip():  # Ensure the topic is not empty
        generate_mcq_from_ncert(topic)
        st.session_state.question_count += 1
    else:
        st.write("Please enter a valid topic or subtopic to generate an MCQ.")

if st.session_state.mcq:
    st.write("**MCQ:**")
    st.write(st.session_state.mcq)
    
    # Display the options
    user_answer = st.radio("Choose your answer:", st.session_state.options)
    
    if st.button("Submit Answer"):
        evaluate_answer(user_answer, st.session_state.correct_answer)
        st.write("**Feedback:** ", st.session_state.feedback)
        if st.session_state.explanation:
            st.write("**Explanation:** ", st.session_state.explanation)

# Display a summary of performance
st.write("### Performance Summary")
st.write(f"Questions Answered: {st.session_state.question_count}")
st.write(f"Correct Answers: {st.session_state.correct_count}")