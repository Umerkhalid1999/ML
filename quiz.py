import streamlit as st
from streamlit_ace import st_ace
import contextlib
import io
import random
import time

# Define coding questions for different levels
easy_questions = [
    {
        "question": """Add Two Integers
        Given two integers num1 and num2, return the sum of the two integers.

        Example 1:
        Input: num1 = 12, num2 = 5
        Output: 17
        Explanation: num1 is 12, num2 is 5, and their sum is 12 + 5 = 17, so 17 is returned.

        Example 2:
        Input: num1 = -10, num2 = 4
        Output: -6
        Explanation: num1 + num2 = -6, so -6 is returned.
        """,
        "code": "def add_two_integers(num1: int, num2: int) -> int:"
    },
]

# Quiz Functionality
def quiz_section():
    start = time.time()
    st.title("Machine Learning Quiz")

    questions = [
        ("Question 1: Machine learning is the subset of following", [
            "1) Artificial Intelligence",
            "2) Deep learning",
            "3) Computer vision",
            "4) Reinforcement Learning"
        ], 1),
        ("Question 2: Machine learning is a subset of?", [
            "1) Intelligence",
            "2) Deep",
            "3) Vision",
            "4) Reinforcement"
        ], 2),
        ("Question 3: What is used to optimize loss functions in machine learning?", [
            "1) Gradient Descent",
            "2) Random Forest",
            "3) K-means",
            "4) Naive Bayes"
        ], 1),
    ]

    correct = 0
    incorrect = 0

    # Display questions and options
    for idx, (question, choices, answer) in enumerate(questions):
        st.write(f"## {question}")
        choice = st.radio(f"Choose your answer for Question {idx + 1}:", choices, key=f"q{idx}")
        if choice.startswith(str(answer)):
            correct += 1
        else:
            incorrect += 1

    # Finish Quiz Button
    if st.button("Finish Quiz"):
        st.success(f"Quiz Completed! Correct: {correct}, Incorrect: {incorrect}")
        st.write(f"Score Percentage: {(correct / len(questions)) * 100:.2f}%")

# Editor Functionality
def code_editor_section():
    st.header("Python Code Editor")

    # Select Difficulty Level
    level = st.radio("Choose your difficulty level:", ("Easy", "Medium", "High"))

    # Pick a random question based on the level
    question = random.choice(easy_questions)
    st.write(f"**Level:** {level}")
    st.write(f"**Question:**\n{question['question']}")

    # Code Editor
    code = st_ace(
        language="python",
        theme="dracula",
        placeholder="Write your Python code here...",
        height=300,
        key="ace_editor",
    )

    # Execute Code Button
    if st.button("Run Code"):
        output = io.StringIO()
        error = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            try:
                exec(code)
            except Exception as e:
                st.error(f"Error: {e}")

        if output.getvalue():
            st.subheader("Output:")
            st.code(output.getvalue())
        if error.getvalue():
            st.subheader("Errors:")
            st.error(error.getvalue())

# Main Application
def main():
    st.sidebar.title("Navigation")
    section = st.sidebar.radio("Go to:", ["Quiz", "Editor"])

    # Display sections based on user selection
    if section == "Quiz":
        st.title("Machine Learning Quiz with Integrated Editor")
        quiz_section()

        # Add toggle button to show/hide editor
        if st.button("Open Code Editor"):
            st.session_state.show_editor = not st.session_state.get("show_editor", False)

        if st.session_state.get("show_editor", False):
            with st.sidebar:
                code_editor_section()

    elif section == "Editor":
        code_editor_section()

if __name__ == "__main__":
    main()
