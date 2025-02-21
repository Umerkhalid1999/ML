import streamlit as st
from streamlit_ace import st_ace
import random
from typing import List

# Python Basic Questions (First 3 shown, total 50)
PYTHON_BASIC = [
    {
        "title": "1. Sum Two Numbers",
        "question": "Write a function that returns the sum of two numbers.",
        "template": """def add_numbers(a: int, b: int) -> int:
    # Your code here
    pass""",
        "test_cases": [
            ((2, 3), 5),
            ((-1, 1), 0),
            ((10, 20), 30)
        ]
    },
    {
        "title": "2. String Reverse",
        "question": "Write a function that reverses a string.",
        "template": """def reverse_string(text: str) -> str:
    # Your code here
    pass""",
        "test_cases": [
            (("hello",), "olleh"),
            (("python",), "nohtyp"),
            (("",), "")
        ]
    },
    {
        "title": "3. Count Vowels",
        "question": "Write a function that counts vowels in a string.",
        "template": """def count_vowels(text: str) -> int:
    # Your code here
    pass""",
        "test_cases": [
            (("hello",), 2),
            (("PYTHON",), 1),
            (("aeiou",), 5)
        ]
    }
]

# Python Intermediate Questions (First 3 shown, total 50)
PYTHON_INTERMEDIATE = [
    {
        "title": "1. List Comprehension",
        "question": "Write a function that returns a list of squares of even numbers from the input list.",
        "template": """def square_evens(numbers: List[int]) -> List[int]:
    # Your code here
    pass""",
        "test_cases": [
            (([1, 2, 3, 4],), [4, 16]),
            (([2, 4, 6],), [4, 16, 36]),
            (([1, 3, 5],), [])
        ]
    },
    {
        "title": "2. Dictionary Manipulation",
        "question": "Write a function that merges two dictionaries and sums values of common keys.",
        "template": """def merge_dicts(dict1: dict, dict2: dict) -> dict:
    # Your code here
    pass""",
        "test_cases": [
            (({"a": 1, "b": 2}, {"b": 3, "c": 4}), {"a": 1, "b": 5, "c": 4}),
            (({}, {"x": 1}), {"x": 1}),
            (({"y": 2}, {}), {"y": 2})
        ]
    },
    {
        "title": "3. List Filtering",
        "question": "Write a function that removes all duplicates from a list while preserving order.",
        "template": """def remove_duplicates(items: List[any]) -> List[any]:
    # Your code here
    pass""",
        "test_cases": [
            (([1, 2, 2, 3, 3, 4],), [1, 2, 3, 4]),
            ((['a', 'b', 'a', 'c'],), ['a', 'b', 'c']),
            (([],), [])
        ]
    }
]

# Python Advanced Questions (First 3 shown, total 50)
PYTHON_ADVANCED = [
    {
        "title": "1. Custom Iterator",
        "question": "Write a function that creates a range iterator with a step parameter.",
        "template": """def custom_range(start: int, end: int, step: int) -> List[int]:
    # Your code here
    pass""",
        "test_cases": [
            ((1, 5, 1), [1, 2, 3, 4]),
            ((0, 10, 2), [0, 2, 4, 6, 8]),
            ((5, 0, -1), [5, 4, 3, 2, 1])
        ]
    },
    {
        "title": "2. Decorator Function",
        "question": "Write a decorator function that caches the results of a function.",
        "template": """def cache_decorator(func):
    # Your code here
    pass

@cache_decorator
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
        "test_cases": [
            ((5,), 5),
            ((7,), 13),
            ((9,), 34)
        ]
    },
    {
        "title": "3. Context Manager",
        "question": "Write a context manager that measures execution time.",
        "template": """class Timer:
    def __enter__(self):
        # Your code here
        pass
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Your code here
        pass""",
        "test_cases": [
            ((), True),  # Simple test to check if context manager works
        ]
    }
]

def run_tests(code: str, test_cases: list) -> bool:
    """Simple test runner that returns True if all tests pass"""
    try:
        # Create namespace for code execution
        namespace = {}
        exec(code, namespace)
        
        # Get the function name
        function_name = code.split('def ')[1].split('(')[0]
        
        # Run all test cases
        for inputs, expected in test_cases:
            result = namespace[function_name](*inputs)
            if result != expected:
                return False
        return True
    except Exception as e:
        return False

def main():
    st.title("Python Coding Practice")
    
    # Level selection
    level = st.selectbox(
        "Select difficulty:",
        ["Basic", "Intermediate", "Advanced"]
    )
    
    # Get questions based on level
    if level == "Basic":
        questions = PYTHON_BASIC
    elif level == "Intermediate":
        questions = PYTHON_INTERMEDIATE
    else:
        questions = PYTHON_ADVANCED
    
    # Question selection
    question = st.selectbox(
        "Select question:",
        range(len(questions)),
        format_func=lambda x: questions[x]["title"]
    )
    
    current_question = questions[question]
    
    # Display question
    st.markdown(f"### Question")
    st.write(current_question["question"])
    
    # Code editor
    code = st_ace(
        value=current_question["template"],
        language="python",
        theme="monokai",
        height=200
    )
    
    # Run tests button
    if st.button("Submit"):
        if run_tests(code, current_question["test_cases"]):
            st.success("✅ All tests passed! Great job!")
        else:
            st.error("❌ Some tests failed. Try again!")

if __name__ == "__main__":
    main()
