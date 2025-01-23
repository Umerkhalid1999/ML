import streamlit as st
from streamlit_ace import st_ace
import contextlib
import io
import random

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

medium_questions = [
    {
        "question": """Find Two Sum
        Given an array of integers nums and an integer target, return the indices of the two numbers that add up to the target.

        Example 1:
        Input: nums = [2, 7, 11, 15], target = 9
        Output: [0, 1]
        Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

        Example 2:
        Input: nums = [3, 2, 4], target = 6
        Output: [1, 2]
        Explanation: Because nums[1] + nums[2] == 6, we return [1, 2].
        """,
        "code": "def two_sum(nums: List[int], target: int) -> List[int]:"
    },
]

high_questions = [
    {
        "question": """Longest Consecutive Sequence
        Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence.

        Example 1:
        Input: nums = [100, 4, 200, 1, 3, 2]
        Output: 4
        Explanation: The longest consecutive elements sequence is [1, 2, 3, 4]. Therefore its length is 4.

        Example 2:
        Input: nums = [0, 0, 1]
        Output: 2
        Explanation: The longest consecutive elements sequence is [0, 1]. Therefore its length is 2.
        """,
        "code": "def longest_consecutive(nums: List[int]) -> int:"
    },
]

# Initialize Streamlit App
def main():
    st.title("Python Coding Practice with Interactive Editor")

    # Let the user choose the difficulty level
    level = st.radio("Choose your difficulty level:", ("Easy", "Medium", "High"))

    # Select a random question based on the chosen level
    if level == "Easy":
        question = random.choice(easy_questions)
    elif level == "Medium":
        question = random.choice(medium_questions)
    else:
        question = random.choice(high_questions)

    # Display the question
    st.write(f"**Level:** {level}")
    st.write(f"**Question:**\n{question['question']}")

    # Ace Editor for Python Code Input
    code = st_ace(
        language="python",
        theme="dracula",
        placeholder="Write your Python code here...",
        height=500,
        key="ace_editor",
    )

    # Button to Execute Code
    if st.button("RUN CODE"):
        # Capture stdout and stderr
        output = io.StringIO()
        error = io.StringIO()

        # Execute the user's code securely
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            try:
                exec(code)
            except Exception as e:
                st.error(f"Error: {e}")

        # Display Output or Errors
        if output.getvalue():
            st.subheader("Output:")
            st.code(output.getvalue())
        if error.getvalue():
            st.subheader("Errors:")
            st.error(error.getvalue())

if __name__ == "__main__":
    main()
