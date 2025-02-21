import streamlit as st
from streamlit_ace import st_ace
import contextlib
import io
import random
import numpy as np
import pandas as pd
from typing import List, Dict, Any
import unittest
import json

# Define different sections of questions
SECTIONS = {
    "Python Basics": "basics",
    "Practice Problems": "practice",
    "Intermediate Python": "intermediate",
    "Machine Learning": "ml",
    "Data Science": "ds"
}

# Python Basics Questions with Test Cases
python_basics = [
    {
        "title": "String Manipulation",
        "question": """
        Write a function that reverses a string without using the built-in reverse function.
        Example:
        Input: "hello"
        Output: "olleh"
        """,
        "code_template": """def reverse_string(s: str) -> str:
    # Your code here
    pass""",
        "test_cases": [
            {"input": ["hello"], "output": "olleh"},
            {"input": ["python"], "output": "nohtyp"},
            {"input": [""], "output": ""}
        ]
    },
    {
        "title": "List Operations",
        "question": """
        Write a function that finds the second largest number in a list.
        Example:
        Input: [10, 5, 8, 12, 3]
        Output: 10
        """,
        "code_template": """def second_largest(nums: List[int]) -> int:
    # Your code here
    pass""",
        "test_cases": [
            {"input": [[10, 5, 8, 12, 3]], "output": 10},
            {"input": [[1, 1, 2]], "output": 1},
            {"input": [[5]], "output": None}
        ]
    }
]

# Practice Problems with Test Cases
practice_problems = [
    {
        "title": "Two Sum",
        "question": """
        Given an array of integers nums and an integer target, return indices of two numbers that add up to target.
        Example:
        Input: nums = [2, 7, 11, 15], target = 9
        Output: [0, 1]
        """,
        "code_template": """def two_sum(nums: List[int], target: int) -> List[int]:
    # Your code here
    pass""",
        "test_cases": [
            {"input": [[2, 7, 11, 15], 9], "output": [0, 1]},
            {"input": [[3, 2, 4], 6], "output": [1, 2]},
            {"input": [[3, 3], 6], "output": [0, 1]}
        ]
    }
]

# ML Questions with Test Cases
ml_questions = [
    {
        "title": "Linear Regression Implementation",
        "question": """
        Implement a simple linear regression model from scratch using gradient descent.
        The function should return predicted y values for the input X.
        Example:
        Input: X = [[1], [2], [3]], y = [2, 4, 6]
        Output: [2.1, 4.0, 5.9] (approximate values)
        """,
        "code_template": """def simple_linear_regression(X: np.ndarray, y: np.ndarray, learning_rate: float = 0.01, epochs: int = 100) -> np.ndarray:
    # Your code here
    pass""",
        "test_cases": [
            {
                "input": [np.array([[1], [2], [3]]), np.array([2, 4, 6])],
                "test_type": "custom",
                "test_function": """
                def test_regression(prediction, actual):
                    return np.allclose(prediction, actual, rtol=0.1)
                """
            }
        ]
    }
]

# Data Science Questions with Test Cases
ds_questions = [
    {
        "title": "Data Cleaning",
        "question": """
        Write a function that cleans a pandas DataFrame by:
        1. Removing duplicate rows
        2. Handling missing values (fill numeric with mean, categorical with mode)
        3. Converting date columns to datetime
        Example input DataFrame has columns: ['name', 'age', 'date', 'category']
        """,
        "code_template": """def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Your code here
    pass""",
        "test_cases": [
            {
                "input": [pd.DataFrame({
                    'name': ['John', 'Jane', 'John', None],
                    'age': [25, None, 25, 30],
                    'date': ['2023-01-01', '2023-02-01', '2023-01-01', '2023-03-01'],
                    'category': ['A', 'B', 'A', None]
                })],
                "test_type": "custom",
                "test_function": """
                def test_cleaning(result_df, input_df):
                    assert result_df.duplicated().sum() == 0
                    assert result_df.isnull().sum().sum() == 0
                    assert pd.api.types.is_datetime64_any_dtype(result_df['date'])
                    return True
                """
            }
        ]
    }
]

class TestRunner:
    @staticmethod
    def run_test_cases(user_code: str, test_cases: List[Dict[str, Any]], function_name: str) -> Dict[str, Any]:
        results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # Create namespace for user code
            namespace = {}
            exec(user_code, namespace)
            user_function = namespace[function_name]
            
            # Run each test case
            for i, test_case in enumerate(test_cases):
                try:
                    if test_case.get("test_type") == "custom":
                        # Execute custom test function
                        test_function_code = test_case["test_function"]
                        test_namespace = {}
                        exec(test_function_code, test_namespace)
                        test_function = test_namespace["test_function"]
                        
                        result = user_function(*test_case["input"])
                        if test_function(result, *test_case["input"]):
                            results["passed"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Test case {i+1} failed")
                    else:
                        # Standard test case
                        result = user_function(*test_case["input"])
                        if result == test_case["output"]:
                            results["passed"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(
                                f"Test case {i+1} failed: Expected {test_case['output']}, got {result}"
                            )
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Test case {i+1} error: {str(e)}")
                    
        except Exception as e:
            results["errors"].append(f"Code execution error: {str(e)}")
            
        return results

def main():
    st.title("🐍 Python Programming Practice Platform")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    section = st.sidebar.radio("Select Section", list(SECTIONS.keys()))
    
    # Main content
    st.header(section)
    
    # Get questions based on selected section
    if section == "Python Basics":
        questions = python_basics
    elif section == "Practice Problems":
        questions = practice_problems
    elif section == "Machine Learning":
        questions = ml_questions
    elif section == "Data Science":
        questions = ds_questions
    else:
        questions = practice_problems  # Default to practice problems
    
    # Question selection
    question_index = st.selectbox(
        "Select Question",
        range(len(questions)),
        format_func=lambda x: questions[x]["title"]
    )
    
    current_question = questions[question_index]
    
    # Display question
    st.markdown("### Problem Statement")
    st.write(current_question["question"])
    
    # Code editor
    st.markdown("### Your Solution")
    code = st_ace(
        value=current_question["code_template"],
        language="python",
        theme="monokai",
        font_size=14,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        height=300
    )
    
    # Test cases execution
    if st.button("Run Tests"):
        with st.spinner("Running tests..."):
            function_name = current_question["code_template"].split("def ")[1].split("(")[0]
            results = TestRunner.run_test_cases(code, current_question["test_cases"], function_name)
            
            # Display results
            st.markdown("### Test Results")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tests Passed", results["passed"])
            with col2:
                st.metric("Tests Failed", results["failed"])
            
            if results["errors"]:
                st.error("Error Details:")
                for error in results["errors"]:
                    st.write(error)
            elif results["failed"] == 0:
                st.success("All tests passed! Great job! 🎉")

if __name__ == "__main__":
    main()
