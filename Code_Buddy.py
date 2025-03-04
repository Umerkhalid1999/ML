import streamlit as st
import streamlit.components.v1 as components
from streamlit_ace import st_ace
import json
import time
import hashlib
import sqlite3
import datetime
import uuid

# Configure page settings
st.set_page_config(layout="wide", page_title="PythonPractice")

# Custom CSS for LeetCode-like styling
st.markdown("""
<style>
    .problem-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .difficulty-easy {
        color: #00b8a3;
        font-weight: bold;
    }
    .difficulty-medium {
        color: #ffc01e;
        font-weight: bold;
    }
    .difficulty-hard {
        color: #ff375f;
        font-weight: bold;
    }
    .success-text {
        color: #00b8a3;
    }
    .failed-text {
        color: #ff375f;
    }
    .stats-box {
        background-color: #f7f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px;
    }
    .example-box {
        background-color: #f7f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .markdown-text {
        font-size: 16px;
        line-height: 1.6;
    }
    .locked-level {
        opacity: 0.5;
        pointer-events: none;
    }
    .level-card {
        padding: 20px;
        border-radius: 5px;
        margin: 10px 0;
        border: 1px solid #ccc;
    }
    .completed-level {
        border-left: 5px solid #00b8a3;
    }
    .current-level {
        border-left: 5px solid #ffc01e;
    }
    .locked-level {
        border-left: 5px solid #ccc;
    }
</style>
""", unsafe_allow_html=True)


# Initialize database
def init_db():
    conn = sqlite3.connect('python_practice.db')
    c = conn.cursor()

    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create user_progress table
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_progress (
        user_id TEXT NOT NULL,
        level INTEGER NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, level),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create submissions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        problem_id TEXT NOT NULL,
        code TEXT NOT NULL,
        passed BOOLEAN NOT NULL,
        execution_time REAL NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()


# Initialize the database
init_db()


# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    conn = sqlite3.connect('python_practice.db')
    c = conn.cursor()

    # Check if username already exists
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, "Username already taken"

    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)

    try:
        c.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
                  (user_id, username, hashed_password))

        # Initialize user progress (unlock level 1)
        c.execute("INSERT INTO user_progress (user_id, level, completed) VALUES (?, ?, ?)",
                  (user_id, 1, False))

        conn.commit()
        conn.close()
        return True, user_id
    except Exception as e:
        conn.close()
        return False, str(e)


def login_user(username, password):
    conn = sqlite3.connect('python_practice.db')
    c = conn.cursor()

    hashed_password = hash_password(password)
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?",
              (username, hashed_password))
    user = c.fetchone()
    conn.close()

    if user:
        return True, user[0]
    return False, "Invalid username or password"


def get_user_level(user_id):
    conn = sqlite3.connect('python_practice.db')
    c = conn.cursor()

    # Get highest unlocked level
    c.execute("SELECT MAX(level) FROM user_progress WHERE user_id = ?", (user_id,))
    max_level = c.fetchone()[0] or 1

    # Get completion status of all levels
    c.execute("SELECT level, completed FROM user_progress WHERE user_id = ?", (user_id,))
    level_status = dict(c.fetchall())

    conn.close()
    return max_level, level_status


def update_user_progress(user_id, level, completed=True):
    conn = sqlite3.connect('python_practice.db')
    c = conn.cursor()

    # Update completion status
    c.execute("""
    INSERT INTO user_progress (user_id, level, completed, last_updated)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(user_id, level) 
    DO UPDATE SET completed = ?, last_updated = CURRENT_TIMESTAMP
    """, (user_id, level, completed, completed))

    # If completed, unlock next level
    if completed:
        c.execute("INSERT OR IGNORE INTO user_progress (user_id, level, completed) VALUES (?, ?, ?)",
                  (user_id, level + 1, False))

    conn.commit()
    conn.close()


def save_submission(user_id, problem_id, code, passed, execution_time):
    conn = sqlite3.connect('python_practice.db')
    c = conn.cursor()

    submission_id = str(uuid.uuid4())

    c.execute("""
    INSERT INTO submissions (id, user_id, problem_id, code, passed, execution_time)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (submission_id, user_id, problem_id, code, passed, execution_time))

    conn.commit()
    conn.close()


# Problem database
# Complete Python Curriculum with 20 Levels
# Complete Python Curriculum with 20 Levels - Simplified
LEVELS = {
1: {
    "name": "Introduction to Python",
    "description": "Learn the very basics of Python programming and execution.",
    "min_problems_to_complete": 2,
    "problems": [
        {
            "id": "hello_world",
            "title": "Hello, World!",
            "difficulty": "Easy",
            "description": "Write a function that returns the string 'Hello, World!' This is traditionally the first program written when learning a new language.",
            "examples": [
                {
                    "input": "",
                    "output": "'Hello, World!'",
                    "explanation": "Your function should return the string 'Hello, World!'"
                }
            ],
            "template": """def hello_world():
    # Write your code here to return "Hello, World!"
    pass""",
            "test_cases": [
                {"input": {}, "output": "Hello, World!"}
            ],
            "hint": "Use the return statement to return the string."
        },
        {
            "id": "python_versions",
            "title": "Python 2 vs Python 3",
            "difficulty": "Easy",
            "description": "Write a function that returns a dictionary listing 3 key differences between Python 2 and Python 3. This is important knowledge for any Python programmer.",
            "examples": [
                {
                    "input": "",
                    "output": "{'difference1': 'Print is a statement in Python 2 but a function in Python 3', 'difference2': 'Division of integers returns integer in Python 2 but float in Python 3', 'difference3': 'Strings are stored as ASCII in Python 2 but Unicode in Python 3'}",
                    "explanation": "Returns a dictionary with 3 key differences between Python 2 and Python 3."
                }
            ],
            "template": """def python_differences():
    # Return a dictionary with 3 key differences between Python 2 and Python 3
    # The keys should be 'difference1', 'difference2', 'difference3'
    # The values should be clear explanations of each difference
    pass""",
            "test_cases": [
                {"input": {}, "output": lambda x: isinstance(x, dict) and len(x) >= 3 and all(key in x for key in ['difference1', 'difference2', 'difference3'])}
            ],
            "hint": "Focus on differences in print syntax, integer division, and string handling."
        },
        {
            "id": "string_formatting",
            "title": "String Formatting",
            "difficulty": "Easy",
            "description": "Write a function that demonstrates three different ways to format strings in Python: using the % operator, the format() method, and f-strings (introduced in Python 3.6).",
            "examples": [
                {
                    "input": "name='John', age=30",
                    "output": "{'percent': 'My name is John and I am 30 years old.', 'format': 'My name is John and I am 30 years old.', 'f_string': 'My name is John and I am 30 years old.'}",
                    "explanation": "Returns a dictionary with the same sentence formatted in three different ways."
                }
            ],
            "template": """def string_formatting_ways(name, age):
    # Return a dictionary with the same sentence formatted in three different ways
    # Keys should be 'percent', 'format', and 'f_string'
    pass""",
            "test_cases": [
                {"input": {"name": "John", "age": 30}, "output": lambda x: isinstance(x, dict) and 'percent' in x and 'format' in x and 'f_string' in x and all('John' in v and '30' in v for v in x.values())}
            ],
            "hint": "Use %s/%d for percent formatting, {}/.format() for the format method, and f'{}' for f-strings."
        },
        {
            "id": "indentation_importance",
            "title": "Indentation Importance",
            "difficulty": "Easy",
            "description": "Write a function that demonstrates the importance of indentation in Python by returning two different results based on indentation.",
            "examples": [
                {
                    "input": "condition=True",
                    "output": "{'indented': 'This will only execute if condition is True', 'not_indented': 'This will always execute regardless of condition'}",
                    "explanation": "Demonstrates how indentation affects execution flow in Python."
                }
            ],
            "template": """def demonstrate_indentation(condition):
    # Return a dictionary showing how indentation affects code execution
    # Keys should be 'indented' and 'not_indented'
    # Use an if statement to demonstrate this principle
    pass""",
            "test_cases": [
                {"input": {"condition": True}, "output": lambda x: isinstance(x, dict) and 'indented' in x and 'not_indented' in x},
                {"input": {"condition": False}, "output": lambda x: isinstance(x, dict) and x.get('indented') == None and 'not_indented' in x}
            ],
            "hint": "Use an if statement and pay attention to what happens when code is indented under the if versus outside the block."
        },
        {
            "id": "basic_data_types",
            "title": "Basic Data Types",
            "difficulty": "Easy",
            "description": "Write a function that demonstrates the basic Python data types (int, float, str, bool, list) by creating a variable of each type and returning them in a dictionary.",
            "examples": [
                {
                    "input": "",
                    "output": "{'integer': 42, 'float': 3.14, 'string': 'hello', 'boolean': True, 'list': [1, 2, 3]}",
                    "explanation": "Returns a dictionary with examples of each basic Python data type."
                }
            ],
            "template": """def basic_types():
    # Create examples of each basic Python data type
    # Return them in a dictionary with keys 'integer', 'float', 'string', 'boolean', and 'list'
    pass""",
            "test_cases": [
                {"input": {}, "output": lambda x: isinstance(x, dict) and isinstance(x.get('integer'), int) and isinstance(x.get('float'), float) and isinstance(x.get('string'), str) and isinstance(x.get('boolean'), bool) and isinstance(x.get('list'), list)}
            ],
            "hint": "Create a variable of each type and add them to a dictionary with the specified keys."
        }
    ]
},
    2: {
        "name": "Variables & Data Types",
        "description": "Learn about different data types in Python and how to use variables.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "check_type",
                "title": "Check Type",
                "difficulty": "Easy",
                "description": "Write a function that returns the type of the input as a string.",
                "examples": [
                    {
                        "input": "value=42",
                        "output": "'int'",
                        "explanation": "Returns 'int' because 42 is an integer."
                    }
                ],
                "template": """def get_type(value):
    # Return the type of the value as a string
    pass""",
                "test_cases": [
                    {"input": {"value": 42}, "output": "int"},
                    {"input": {"value": "hello"}, "output": "str"},
                    {"input": {"value": 3.14}, "output": "float"}
                ],
                "hint": "Use the type() function and convert the result to a string."
            },
            {
                "id": "convert_to_int",
                "title": "Convert to Integer",
                "difficulty": "Easy",
                "description": "Write a function that converts a string to an integer.",
                "examples": [
                    {
                        "input": "text='42'",
                        "output": "42",
                        "explanation": "Converts the string '42' to the integer 42."
                    }
                ],
                "template": """def to_integer(text):
    # Convert the string to an integer and return it
    pass""",
                "test_cases": [
                    {"input": {"text": "42"}, "output": 42},
                    {"input": {"text": "-10"}, "output": -10}
                ],
                "hint": "Use the int() function to convert a string to an integer."
            },
            {
                "id": "area_calculator",
                "title": "Area Calculator",
                "difficulty": "Easy",
                "description": "Write a function that calculates the area of a rectangle.",
                "examples": [
                    {
                        "input": "length=5, width=3",
                        "output": "15",
                        "explanation": "The area of a rectangle with length 5 and width 3 is 15."
                    }
                ],
                "template": """def calculate_area(length, width):
    # Calculate and return the area of the rectangle
    pass""",
                "test_cases": [
                    {"input": {"length": 5, "width": 3}, "output": 15},
                    {"input": {"length": 4, "width": 4}, "output": 16}
                ],
                "hint": "Multiply the length by the width to calculate the area."
            }
        ]
    },
    3: {
        "name": "String Operations",
        "description": "Learn about string manipulation and operations in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "concat_strings",
                "title": "Concatenate Strings",
                "difficulty": "Easy",
                "description": "Write a function that concatenates two strings with a space between them.",
                "examples": [
                    {
                        "input": "str1='Hello', str2='World'",
                        "output": "'Hello World'",
                        "explanation": "Concatenates 'Hello' and 'World' with a space in between."
                    }
                ],
                "template": """def concatenate(str1, str2):
    # Concatenate the strings with a space between them
    pass""",
                "test_cases": [
                    {"input": {"str1": "Hello", "str2": "World"}, "output": "Hello World"},
                    {"input": {"str1": "Python", "str2": "Programming"}, "output": "Python Programming"}
                ],
                "hint": "Use the + operator with strings and include a space character between them."
            },
            {
                "id": "string_length",
                "title": "String Length",
                "difficulty": "Easy",
                "description": "Write a function that returns the length of a string.",
                "examples": [
                    {
                        "input": "text='Python'",
                        "output": "6",
                        "explanation": "The string 'Python' has 6 characters."
                    }
                ],
                "template": """def get_length(text):
    # Return the length of the string
    pass""",
                "test_cases": [
                    {"input": {"text": "Python"}, "output": 6},
                    {"input": {"text": "Hello World"}, "output": 11}
                ],
                "hint": "Use the len() function to get the length of a string."
            },
            {
                "id": "reverse_string",
                "title": "Reverse String",
                "difficulty": "Easy",
                "description": "Write a function that reverses a string.",
                "examples": [
                    {
                        "input": "text='Python'",
                        "output": "'nohtyP'",
                        "explanation": "Returns 'Python' in reverse order."
                    }
                ],
                "template": """def reverse(text):
    # Return the reversed string
    pass""",
                "test_cases": [
                    {"input": {"text": "Python"}, "output": "nohtyP"},
                    {"input": {"text": "Hello"}, "output": "olleH"}
                ],
                "hint": "You can use string slicing with a negative step: text[::-1]"
            }
        ]
    },
    4: {
        "name": "Operators",
        "description": "Learn about arithmetic, comparison, and logical operators in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "basic_math",
                "title": "Basic Math Operations",
                "difficulty": "Easy",
                "description": "Write a function that performs addition, subtraction, multiplication, and division on two numbers.",
                "examples": [
                    {
                        "input": "a=10, b=5",
                        "output": "{'sum': 15, 'difference': 5, 'product': 50, 'quotient': 2.0}",
                        "explanation": "Returns a dictionary with the results of each operation."
                    }
                ],
                "template": """def math_operations(a, b):
    # Return a dictionary with the results of basic math operations
    pass""",
                "test_cases": [
                    {"input": {"a": 10, "b": 5}, "output": {"sum": 15, "difference": 5, "product": 50, "quotient": 2.0}},
                    {"input": {"a": 8, "b": 4}, "output": {"sum": 12, "difference": 4, "product": 32, "quotient": 2.0}}
                ],
                "hint": "Perform each operation and store the results in a dictionary."
            },
            {
                "id": "compare_nums",
                "title": "Compare Numbers",
                "difficulty": "Easy",
                "description": "Write a function that returns True if the first number is greater than the second number, otherwise False.",
                "examples": [
                    {
                        "input": "a=10, b=5",
                        "output": "True",
                        "explanation": "Returns True because 10 is greater than 5."
                    }
                ],
                "template": """def is_greater(a, b):
    # Return True if a > b, otherwise False
    pass""",
                "test_cases": [
                    {"input": {"a": 10, "b": 5}, "output": True},
                    {"input": {"a": 5, "b": 10}, "output": False},
                    {"input": {"a": 5, "b": 5}, "output": False}
                ],
                "hint": "Use the > operator to compare the two numbers."
            },
            {
                "id": "logical_and",
                "title": "Logical AND",
                "difficulty": "Easy",
                "description": "Write a function that returns True if both inputs are True, otherwise False.",
                "examples": [
                    {
                        "input": "a=True, b=True",
                        "output": "True",
                        "explanation": "Returns True because both inputs are True."
                    }
                ],
                "template": """def logical_and(a, b):
    # Return True if both a and b are True, otherwise False
    pass""",
                "test_cases": [
                    {"input": {"a": True, "b": True}, "output": True},
                    {"input": {"a": True, "b": False}, "output": False},
                    {"input": {"a": False, "b": False}, "output": False}
                ],
                "hint": "Use the 'and' keyword to combine the two conditions."
            }
        ]
    },
    5: {
        "name": "Conditional Statements",
        "description": "Learn to use if, elif, and else statements for decision making.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "check_even",
                "title": "Check Even",
                "difficulty": "Easy",
                "description": "Write a function that checks if a number is even.",
                "examples": [
                    {
                        "input": "num=4",
                        "output": "True",
                        "explanation": "Returns True because 4 is an even number."
                    }
                ],
                "template": """def is_even(num):
    # Return True if num is even, otherwise False
    pass""",
                "test_cases": [
                    {"input": {"num": 4}, "output": True},
                    {"input": {"num": 7}, "output": False},
                    {"input": {"num": 0}, "output": True}
                ],
                "hint": "A number is even if it's divisible by 2 (i.e., num % 2 == 0)."
            },
            {
                "id": "max_of_three",
                "title": "Maximum of Three Numbers",
                "difficulty": "Easy",
                "description": "Write a function that returns the largest of three numbers.",
                "examples": [
                    {
                        "input": "a=5, b=10, c=3",
                        "output": "10",
                        "explanation": "Returns 10 because it's the largest number among 5, 10, and 3."
                    }
                ],
                "template": """def find_max(a, b, c):
    # Return the largest of the three numbers
    pass""",
                "test_cases": [
                    {"input": {"a": 5, "b": 10, "c": 3}, "output": 10},
                    {"input": {"a": 15, "b": 5, "c": 8}, "output": 15},
                    {"input": {"a": 5, "b": 5, "c": 10}, "output": 10}
                ],
                "hint": "Use if-elif-else statements to compare the three numbers."
            },
            {
                "id": "grade_letter",
                "title": "Grade Letter",
                "difficulty": "Easy",
                "description": "Write a function that converts a numerical score to a letter grade.",
                "examples": [
                    {
                        "input": "score=85",
                        "output": "'B'",
                        "explanation": "Returns 'B' for a score of 85 (80-89)."
                    }
                ],
                "template": """def get_grade(score):
    # Convert score to letter grade: A (90-100), B (80-89), C (70-79), D (60-69), F (0-59)
    pass""",
                "test_cases": [
                    {"input": {"score": 95}, "output": "A"},
                    {"input": {"score": 85}, "output": "B"},
                    {"input": {"score": 75}, "output": "C"},
                    {"input": {"score": 65}, "output": "D"},
                    {"input": {"score": 55}, "output": "F"}
                ],
                "hint": "Use if-elif-else statements to check the score ranges."
            }
        ]
    },
    6: {
        "name": "Loops",
        "description": "Learn to use for and while loops for repetitive tasks.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "sum_list",
                "title": "Sum of List",
                "difficulty": "Easy",
                "description": "Write a function that calculates the sum of all numbers in a list.",
                "examples": [
                    {
                        "input": "numbers=[1, 2, 3, 4, 5]",
                        "output": "15",
                        "explanation": "Returns the sum of all numbers in the list: 1 + 2 + 3 + 4 + 5 = 15."
                    }
                ],
                "template": """def sum_numbers(numbers):
    # Calculate and return the sum of all numbers in the list
    pass""",
                "test_cases": [
                    {"input": {"numbers": [1, 2, 3, 4, 5]}, "output": 15},
                    {"input": {"numbers": [10, 20, 30]}, "output": 60},
                    {"input": {"numbers": []}, "output": 0}
                ],
                "hint": "Use a for loop to iterate through the list and add each number to a running total."
            },
            {
                "id": "count_down",
                "title": "Countdown",
                "difficulty": "Easy",
                "description": "Write a function that returns a list of numbers counting down from n to 1.",
                "examples": [
                    {
                        "input": "n=5",
                        "output": "[5, 4, 3, 2, 1]",
                        "explanation": "Returns a list counting down from 5 to 1."
                    }
                ],
                "template": """def countdown(n):
    # Return a list counting down from n to 1
    pass""",
                "test_cases": [
                    {"input": {"n": 5}, "output": [5, 4, 3, 2, 1]},
                    {"input": {"n": 3}, "output": [3, 2, 1]},
                    {"input": {"n": 1}, "output": [1]}
                ],
                "hint": "Use a for loop with the range function to generate the countdown sequence."
            },
            {
                "id": "multiply_list",
                "title": "Multiply List",
                "difficulty": "Easy",
                "description": "Write a function that multiplies each number in a list by a given factor.",
                "examples": [
                    {
                        "input": "numbers=[1, 2, 3, 4], factor=2",
                        "output": "[2, 4, 6, 8]",
                        "explanation": "Returns a new list where each number is multiplied by 2."
                    }
                ],
                "template": """def multiply_by(numbers, factor):
    # Multiply each number in the list by the factor
    # Return the new list
    pass""",
                "test_cases": [
                    {"input": {"numbers": [1, 2, 3, 4], "factor": 2}, "output": [2, 4, 6, 8]},
                    {"input": {"numbers": [5, 10, 15], "factor": 3}, "output": [15, 30, 45]},
                    {"input": {"numbers": [], "factor": 5}, "output": []}
                ],
                "hint": "Use a for loop to iterate through the list and create a new list with the multiplied values."
            }
        ]
    },
    7: {
        "name": "Lists",
        "description": "Learn to work with lists in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "find_max",
                "title": "Find Maximum",
                "difficulty": "Easy",
                "description": "Write a function that finds the maximum value in a list.",
                "examples": [
                    {
                        "input": "numbers=[5, 8, 3, 10, 2]",
                        "output": "10",
                        "explanation": "Returns 10, which is the largest number in the list."
                    }
                ],
                "template": """def find_maximum(numbers):
    # Find and return the maximum value in the list
    pass""",
                "test_cases": [
                    {"input": {"numbers": [5, 8, 3, 10, 2]}, "output": 10},
                    {"input": {"numbers": [-5, -10, -3]}, "output": -3},
                    {"input": {"numbers": [7]}, "output": 7}
                ],
                "hint": "Use a for loop to iterate through the list and keep track of the maximum value found so far, or use the built-in max() function."
            },
            {
                "id": "filter_evens",
                "title": "Filter Even Numbers",
                "difficulty": "Easy",
                "description": "Write a function that filters out all the even numbers from a list.",
                "examples": [
                    {
                        "input": "numbers=[1, 2, 3, 4, 5, 6]",
                        "output": "[2, 4, 6]",
                        "explanation": "Returns a list containing only the even numbers from the input list."
                    }
                ],
                "template": """def get_even_numbers(numbers):
    # Return a list containing only the even numbers from the input list
    pass""",
                "test_cases": [
                    {"input": {"numbers": [1, 2, 3, 4, 5, 6]}, "output": [2, 4, 6]},
                    {"input": {"numbers": [1, 3, 5]}, "output": []},
                    {"input": {"numbers": [2, 4, 6]}, "output": [2, 4, 6]}
                ],
                "hint": "Use a for loop to iterate through the list and check if each number is even (num % 2 == 0)."
            },
            {
                "id": "join_lists",
                "title": "Join Lists",
                "difficulty": "Easy",
                "description": "Write a function that combines two lists into one.",
                "examples": [
                    {
                        "input": "list1=[1, 2, 3], list2=[4, 5, 6]",
                        "output": "[1, 2, 3, 4, 5, 6]",
                        "explanation": "Returns a new list containing all elements from both input lists."
                    }
                ],
                "template": """def combine_lists(list1, list2):
    # Combine the two lists into one and return it
    pass""",
                "test_cases": [
                    {"input": {"list1": [1, 2, 3], "list2": [4, 5, 6]}, "output": [1, 2, 3, 4, 5, 6]},
                    {"input": {"list1": [], "list2": [1, 2, 3]}, "output": [1, 2, 3]},
                    {"input": {"list1": [1, 2, 3], "list2": []}, "output": [1, 2, 3]}
                ],
                "hint": "Use the + operator to concatenate the lists, or extend one list with the other."
            }
        ]
    },
    8: {
        "name": "List Comprehension",
        "description": "Learn to use list comprehensions for concise list creation.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "squares_list",
                "title": "List of Squares",
                "difficulty": "Easy",
                "description": "Write a function that returns a list of squares of numbers from 1 to n.",
                "examples": [
                    {
                        "input": "n=5",
                        "output": "[1, 4, 9, 16, 25]",
                        "explanation": "Returns a list containing the squares of numbers from 1 to 5."
                    }
                ],
                "template": """def get_squares(n):
    # Return a list of squares of numbers from 1 to n using list comprehension
    pass""",
                "test_cases": [
                    {"input": {"n": 5}, "output": [1, 4, 9, 16, 25]},
                    {"input": {"n": 3}, "output": [1, 4, 9]},
                    {"input": {"n": 1}, "output": [1]}
                ],
                "hint": "Use a list comprehension with the format [x**2 for x in range(1, n+1)]."
            },
            {
                "id": "filter_positive",
                "title": "Filter Positive Numbers",
                "difficulty": "Easy",
                "description": "Write a function that filters out all positive numbers from a list.",
                "examples": [
                    {
                        "input": "numbers=[-2, -1, 0, 1, 2]",
                        "output": "[1, 2]",
                        "explanation": "Returns a list containing only the positive numbers from the input list."
                    }
                ],
                "template": """def get_positives(numbers):
    # Return a list containing only the positive numbers using list comprehension
    pass""",
                "test_cases": [
                    {"input": {"numbers": [-2, -1, 0, 1, 2]}, "output": [1, 2]},
                    {"input": {"numbers": [-3, -2, -1]}, "output": []},
                    {"input": {"numbers": [1, 2, 3]}, "output": [1, 2, 3]}
                ],
                "hint": "Use a list comprehension with a condition to filter for positive numbers: [x for x in numbers if x > 0]."
            },
            {
                "id": "double_list",
                "title": "Double Values",
                "difficulty": "Easy",
                "description": "Write a function that doubles all the values in a list.",
                "examples": [
                    {
                        "input": "numbers=[1, 2, 3, 4]",
                        "output": "[2, 4, 6, 8]",
                        "explanation": "Returns a list where each number is doubled."
                    }
                ],
                "template": """def double_values(numbers):
    # Return a list where each value is doubled using list comprehension
    pass""",
                "test_cases": [
                    {"input": {"numbers": [1, 2, 3, 4]}, "output": [2, 4, 6, 8]},
                    {"input": {"numbers": [0, 5, 10]}, "output": [0, 10, 20]},
                    {"input": {"numbers": []}, "output": []}
                ],
                "hint": "Use a list comprehension that multiplies each value by 2: [x * 2 for x in numbers]."
            }
        ]
    },
    9: {
        "name": "Dictionaries",
        "description": "Learn to work with dictionaries in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "create_dict",
                "title": "Create Dictionary",
                "difficulty": "Easy",
                "description": "Write a function that creates a dictionary from two lists - one of keys and one of values.",
                "examples": [
                    {
                        "input": "keys=['a', 'b', 'c'], values=[1, 2, 3]",
                        "output": "{'a': 1, 'b': 2, 'c': 3}",
                        "explanation": "Returns a dictionary with keys from the first list and corresponding values from the second list."
                    }
                ],
                "template": """def create_dictionary(keys, values):
    # Create and return a dictionary from the two lists
    pass""",
                "test_cases": [
                    {"input": {"keys": ['a', 'b', 'c'], "values": [1, 2, 3]}, "output": {'a': 1, 'b': 2, 'c': 3}},
                    {"input": {"keys": ['name', 'age'], "values": ['John', 25]}, "output": {'name': 'John', 'age': 25}},
                    {"input": {"keys": [], "values": []}, "output": {}}
                ],
                "hint": "Use the zip() function to pair up the keys and values, then convert to a dictionary."
            },
            {
                "id": "dict_value",
                "title": "Get Dictionary Value",
                "difficulty": "Easy",
                "description": "Write a function that returns the value for a given key in a dictionary, with a default value if the key doesn't exist.",
                "examples": [
                    {
                        "input": "dictionary={'a': 1, 'b': 2, 'c': 3}, key='b', default=0",
                        "output": "2",
                        "explanation": "Returns the value for key 'b', which is 2."
                    }
                ],
                "template": """def get_value(dictionary, key, default=None):
    # Return the value for the key, or the default value if the key doesn't exist
    pass""",
                "test_cases": [
                    {"input": {"dictionary": {'a': 1, 'b': 2, 'c': 3}, "key": 'b', "default": 0}, "output": 2},
                    {"input": {"dictionary": {'a': 1, 'b': 2, 'c': 3}, "key": 'd', "default": 0}, "output": 0},
                    {"input": {"dictionary": {}, "key": 'a', "default": 'Not found'}, "output": 'Not found'}
                ],
                "hint": "Use the get() method of dictionaries, which accepts a default value."
            },
            {
                "id": "count_items",
                "title": "Count Items",
                "difficulty": "Easy",
                "description": "Write a function that counts the occurrence of each item in a list and returns a dictionary.",
                "examples": [
                    {
                        "input": "items=['a', 'b', 'a', 'c', 'b', 'a']",
                        "output": "{'a': 3, 'b': 2, 'c': 1}",
                        "explanation": "Returns a dictionary with each item as a key and its count as the value."
                    }
                ],
                "template": """def count_occurrences(items):
    # Count occurrences of each item and return a dictionary
    pass""",
                "test_cases": [
                    {"input": {"items": ['a', 'b', 'a', 'c', 'b', 'a']}, "output": {'a': 3, 'b': 2, 'c': 1}},
                    {"input": {"items": [1, 2, 3, 1, 2, 1]}, "output": {1: 3, 2: 2, 3: 1}},
                    {"input": {"items": []}, "output": {}}
                ],
                "hint": "Initialize an empty dictionary, then iterate through the list, incrementing the count for each item."
            }
        ]
    },
    10: {
        "name": "Functions",
        "description": "Learn advanced function concepts in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "default_param",
                "title": "Default Parameters",
                "difficulty": "Easy",
                "description": "Write a function that greets a person with an optional greeting.",
                "examples": [
                    {
                        "input": "name='John', greeting='Hello'",
                        "output": "'Hello, John!'",
                        "explanation": "Returns a greeting with the provided name and greeting."
                    }
                ],
                "template": """def greet_person(name, greeting='Hello'):
    # Return a greeting with the name and optional greeting
    pass""",
                "test_cases": [
                    {"input": {"name": "John", "greeting": "Hello"}, "output": "Hello, John!"},
                    {"input": {"name": "Alice"}, "output": "Hello, Alice!"},
                    {"input": {"name": "Alice"}, "output": "Hello, Alice!"},
                    {"input": {"name": "Bob", "greeting": "Hi"}, "output": "Hi, Bob!"}
                ],
                "hint": "Use string formatting or concatenation to combine the greeting and name."
            },
            {
                "id": "multiple_return",
                "title": "Multiple Return Values",
                "difficulty": "Easy",
                "description": "Write a function that returns both the minimum and maximum values in a list.",
                "examples": [
                    {
                        "input": "numbers=[1, 5, 3, 9, 2]",
                        "output": "(1, 9)",
                        "explanation": "Returns a tuple with the minimum value (1) and maximum value (9) from the list."
                    }
                ],
                "template": """def min_max(numbers):
    # Return a tuple containing the minimum and maximum values
    pass""",
                "test_cases": [
                    {"input": {"numbers": [1, 5, 3, 9, 2]}, "output": (1, 9)},
                    {"input": {"numbers": [5, 5, 5, 5]}, "output": (5, 5)},
                    {"input": {"numbers": [-10, 0, 10]}, "output": (-10, 10)}
                ],
                "hint": "Use the built-in min() and max() functions and return their results as a tuple."
            },
            {
                "id": "recursive_sum",
                "title": "Recursive Sum",
                "difficulty": "Medium",
                "description": "Write a recursive function that calculates the sum of all numbers from 1 to n.",
                "examples": [
                    {
                        "input": "n=5",
                        "output": "15",
                        "explanation": "Returns the sum 1 + 2 + 3 + 4 + 5 = 15, calculated recursively."
                    }
                ],
                "template": """def sum_to_n(n):
    # Calculate the sum from 1 to n recursively
    pass""",
                "test_cases": [
                    {"input": {"n": 5}, "output": 15},
                    {"input": {"n": 1}, "output": 1},
                    {"input": {"n": 0}, "output": 0}
                ],
                "hint": "Base case: if n is 0 or 1. Recursive case: n + sum_to_n(n-1)."
            }
        ]
    },
    11: {
        "name": "Error Handling",
        "description": "Learn how to handle errors and exceptions in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "safe_divide",
                "title": "Safe Division",
                "difficulty": "Easy",
                "description": "Write a function that safely divides two numbers, handling division by zero.",
                "examples": [
                    {
                        "input": "a=10, b=2",
                        "output": "5.0",
                        "explanation": "Returns 10 divided by 2, which is 5.0."
                    }
                ],
                "template": """def divide_safely(a, b):
    # Divide a by b, handling division by zero by returning None
    pass""",
                "test_cases": [
                    {"input": {"a": 10, "b": 2}, "output": 5.0},
                    {"input": {"a": 10, "b": 0}, "output": None},
                    {"input": {"a": 0, "b": 5}, "output": 0.0}
                ],
                "hint": "Use a try-except block to catch ZeroDivisionError."
            },
            {
                "id": "int_converter",
                "title": "Integer Converter",
                "difficulty": "Easy",
                "description": "Write a function that converts a string to an integer, handling invalid inputs.",
                "examples": [
                    {
                        "input": "text='123'",
                        "output": "123",
                        "explanation": "Returns the integer value of the string '123'."
                    }
                ],
                "template": """def convert_to_int(text):
    # Convert the string to an integer, returning None if conversion fails
    pass""",
                "test_cases": [
                    {"input": {"text": "123"}, "output": 123},
                    {"input": {"text": "-45"}, "output": -45},
                    {"input": {"text": "abc"}, "output": None}
                ],
                "hint": "Use a try-except block to catch ValueError when converting fails."
            },
            {
                "id": "file_reader",
                "title": "Safe File Reader",
                "difficulty": "Medium",
                "description": "Write a function that safely reads a file, handling file not found errors.",
                "examples": [
                    {
                        "input": "filename='sample.txt'",
                        "output": "'File contents...'",
                        "explanation": "Returns the contents of the file, or an error message if the file doesn't exist."
                    }
                ],
                "template": """def read_file_safely(filename):
    # Try to read and return the contents of the file
    # Return 'File not found' if the file doesn't exist
    pass""",
                "test_cases": [
                    {"input": {"filename": "nonexistent.txt"}, "output": "File not found"},
                    {"input": {"filename": "sample.txt"},
                     "output": lambda x: isinstance(x, str) and x != "File not found"}
                ],
                "hint": "Use a try-except block to catch FileNotFoundError when opening the file."
            }
        ]
    },
    12: {
        "name": "File I/O",
        "description": "Learn to read from and write to files in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "write_file",
                "title": "Write to File",
                "difficulty": "Easy",
                "description": "Write a function that writes content to a file.",
                "examples": [
                    {
                        "input": "filename='output.txt', content='Hello, World!'",
                        "output": "True",
                        "explanation": "Writes 'Hello, World!' to a file named 'output.txt' and returns True if successful."
                    }
                ],
                "template": """def write_to_file(filename, content):
    # Write the content to the file and return True if successful, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"filename": "output.txt", "content": "Hello, World!"}, "output": True}
                ],
                "hint": "Use the open() function with mode 'w' to write to the file."
            },
            {
                "id": "read_lines",
                "title": "Read File Lines",
                "difficulty": "Easy",
                "description": "Write a function that reads a file and returns its contents as a list of lines.",
                "examples": [
                    {
                        "input": "filename='sample.txt'",
                        "output": "['Line 1', 'Line 2', 'Line 3']",
                        "explanation": "Reads the contents of 'sample.txt' and returns each line as an element in a list."
                    }
                ],
                "template": """def read_file_lines(filename):
    # Read the file and return its contents as a list of lines
    # Return an empty list if the file doesn't exist
    pass""",
                "test_cases": [
                    {"input": {"filename": "sample.txt"}, "output": lambda x: isinstance(x, list)},
                    {"input": {"filename": "nonexistent.txt"}, "output": []}
                ],
                "hint": "Use the open() function with mode 'r' and the readlines() method to read the file."
            },
            {
                "id": "file_stats",
                "title": "File Statistics",
                "difficulty": "Medium",
                "description": "Write a function that counts the number of characters, words, and lines in a file.",
                "examples": [
                    {
                        "input": "filename='sample.txt'",
                        "output": "{'characters': 20, 'words': 5, 'lines': 2}",
                        "explanation": "Returns statistics about the contents of the file."
                    }
                ],
                "template": """def get_file_stats(filename):
    # Return a dictionary with character, word, and line counts for the file
    # Return empty counts if the file doesn't exist
    pass""",
                "test_cases": [
                    {"input": {"filename": "sample.txt"},
                     "output": lambda x: isinstance(x, dict) and "characters" in x and "words" in x and "lines" in x},
                    {"input": {"filename": "nonexistent.txt"}, "output": {"characters": 0, "words": 0, "lines": 0}}
                ],
                "hint": "Read the file and use string methods to count characters, words, and lines."
            }
        ]
    },
    13: {
        "name": "Modules",
        "description": "Learn to use Python's built-in modules.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "math_operations",
                "title": "Math Module Operations",
                "difficulty": "Easy",
                "description": "Write a function that performs various mathematical operations using the math module.",
                "examples": [
                    {
                        "input": "x=4",
                        "output": "{'square_root': 2.0, 'cube_root': 1.59, 'cosine': 1.0}",
                        "explanation": "Returns the results of different mathematical operations on the input number."
                    }
                ],
                "template": """def math_ops(x):
    # Use the math module to calculate and return square root, cube root, and cosine(0)
    import math

    # Your code here
    pass""",
                "test_cases": [
                    {"input": {"x": 4},
                     "output": lambda d: abs(d["square_root"] - 2.0) < 0.01 and abs(d["cosine"] - 1.0) < 0.01},
                    {"input": {"x": 9}, "output": lambda d: abs(d["square_root"] - 3.0) < 0.01}
                ],
                "hint": "Import the math module and use math.sqrt(), math.pow() for cube root, and math.cos()."
            },
            {
                "id": "random_generator",
                "title": "Random Number Generator",
                "difficulty": "Easy",
                "description": "Write a function that generates a list of random numbers using the random module.",
                "examples": [
                    {
                        "input": "n=5, min_val=1, max_val=10",
                        "output": "[3, 8, 5, 1, 9]",
                        "explanation": "Returns a list of 5 random integers between 1 and 10."
                    }
                ],
                "template": """def generate_random_numbers(n, min_val, max_val):
    # Generate a list of n random integers between min_val and max_val
    import random

    # Your code here
    pass""",
                "test_cases": [
                    {"input": {"n": 5, "min_val": 1, "max_val": 10},
                     "output": lambda x: len(x) == 5 and all(1 <= num <= 10 for num in x)},
                    {"input": {"n": 3, "min_val": -5, "max_val": 5},
                     "output": lambda x: len(x) == 3 and all(-5 <= num <= 5 for num in x)}
                ],
                "hint": "Import the random module and use random.randint() in a loop to generate random numbers."
            },
            {
                "id": "datetime_converter",
                "title": "Date and Time Converter",
                "difficulty": "Medium",
                "description": "Write a function that converts a date string to different formats using the datetime module.",
                "examples": [
                    {
                        "input": "date_str='2023-01-15'",
                        "output": "{'day_of_week': 'Sunday', 'month_name': 'January', 'formatted': '01/15/2023'}",
                        "explanation": "Returns information about the given date in different formats."
                    }
                ],
                "template": """def convert_date(date_str):
    # Convert the date string (YYYY-MM-DD) to different formats using datetime
    from datetime import datetime

    # Your code here
    pass""",
                "test_cases": [
                    {"input": {"date_str": "2023-01-15"}, "output": lambda x: isinstance(x,
                                                                                         dict) and "day_of_week" in x and "month_name" in x and "formatted" in x},
                    {"input": {"date_str": "2022-12-25"},
                     "output": lambda x: isinstance(x, dict) and x["day_of_week"] == "Sunday" and x[
                         "month_name"] == "December"}
                ],
                "hint": "Use datetime.strptime() to parse the string, and various methods and properties to extract information."
            }
        ]
    },
    14: {
        "name": "Classes and Objects",
        "description": "Learn object-oriented programming with classes in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "rectangle_class",
                "title": "Rectangle Class",
                "difficulty": "Easy",
                "description": "Create a Rectangle class with methods to calculate area and perimeter.",
                "examples": [
                    {
                        "input": "Rectangle(width=5, height=3)",
                        "output": "Area: 15, Perimeter: 16",
                        "explanation": "Creates a Rectangle object with width 5 and height 3, then calculates its area and perimeter."
                    }
                ],
                "template": """class Rectangle:
    # Create a Rectangle class with attributes for width and height
    # Include methods to calculate area and perimeter
    pass

def test_rectangle(width, height):
    # Create a Rectangle object and test its methods
    # Return a string with the area and perimeter
    pass""",
                "test_cases": [
                    {"input": {"width": 5, "height": 3}, "output": "Area: 15, Perimeter: 16"},
                    {"input": {"width": 4, "height": 4}, "output": "Area: 16, Perimeter: 16"}
                ],
                "hint": "Define __init__ to set width and height, then create area() and perimeter() methods."
            },
            {
                "id": "bank_account",
                "title": "Bank Account Class",
                "difficulty": "Easy",
                "description": "Create a BankAccount class with methods to deposit, withdraw, and check balance.",
                "examples": [
                    {
                        "input": "BankAccount(1000).deposit(500).withdraw(200).get_balance()",
                        "output": "1300",
                        "explanation": "Creates a BankAccount with initial balance 1000, deposits 500, withdraws 200, and returns the final balance."
                    }
                ],
                "template": """class BankAccount:
    # Create a BankAccount class with an initial balance
    # Include methods to deposit, withdraw, and get balance
    pass

def test_bank_account(initial_balance, deposit_amount, withdraw_amount):
    # Create a BankAccount object and test its methods
    # Return the final balance
    pass""",
                "test_cases": [
                    {"input": {"initial_balance": 1000, "deposit_amount": 500, "withdraw_amount": 200}, "output": 1300},
                    {"input": {"initial_balance": 100, "deposit_amount": 50, "withdraw_amount": 150}, "output": 0}
                ],
                "hint": "Define __init__ to set the initial balance, then implement deposit(), withdraw(), and get_balance() methods."
            },
            {
                "id": "simple_stack",
                "title": "Stack Class",
                "difficulty": "Medium",
                "description": "Create a Stack class with methods to push, pop, and check if empty.",
                "examples": [
                    {
                        "input": "Stack().push(1).push(2).pop()",
                        "output": "2",
                        "explanation": "Creates a Stack, pushes 1 and 2 onto it, then pops and returns the top element (2)."
                    }
                ],
                "template": """class Stack:
    # Create a Stack class with methods to push, pop, and is_empty
    pass

def test_stack(operations):
    # Create a Stack object and test its methods based on the operations list
    # Operations can be: 'push X', 'pop', 'is_empty'
    # Return a list of results
    pass""",
                "test_cases": [
                    {"input": {"operations": ["push 1", "push 2", "pop", "is_empty"]},
                     "output": [None, None, 2, False]},
                    {"input": {"operations": ["is_empty", "push 5", "is_empty"]}, "output": [True, None, False]}
                ],
                "hint": "Use a list to store the stack elements. push() adds to the end, pop() removes and returns the last element, is_empty() checks if the list is empty."
            }
        ]
    },
    15: {
        "name": "Inheritance",
        "description": "Learn about inheritance in object-oriented programming.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "animal_inheritance",
                "title": "Animal Inheritance",
                "difficulty": "Easy",
                "description": "Create a base Animal class and derived Dog and Cat classes.",
                "examples": [
                    {
                        "input": "Dog('Buddy').speak()",
                        "output": "'Buddy says Woof!'",
                        "explanation": "Creates a Dog object with name 'Buddy' and calls its speak method."
                    }
                ],
                "template": """class Animal:
    # Create a base Animal class with a name attribute and speak method
    pass

class Dog(Animal):
    # Create a Dog class that inherits from Animal
    pass

class Cat(Animal):
    # Create a Cat class that inherits from Animal
    pass

def test_animals(animal_type, name):
    # Create an animal of the specified type and test its methods
    # Return the result of calling speak()
    pass""",
                "test_cases": [
                    {"input": {"animal_type": "dog", "name": "Buddy"}, "output": "Buddy says Woof!"},
                    {"input": {"animal_type": "cat", "name": "Whiskers"}, "output": "Whiskers says Meow!"}
                ],
                "hint": "Define the Animal class with an __init__ method that takes a name parameter. Override the speak method in derived classes."
            },
            {
                "id": "shape_inheritance",
                "title": "Shape Inheritance",
                "difficulty": "Medium",
                "description": "Create a base Shape class with derived Circle and Rectangle classes.",
                "examples": [
                    {
                        "input": "Circle(radius=5).area()",
                        "output": "78.54",
                        "explanation": "Creates a Circle object with radius 5 and calculates its area."
                    }
                ],
                "template": """class Shape:
    # Create a base Shape class with an area method
    pass

class Circle(Shape):
    # Create a Circle class that inherits from Shape
    pass

class Rectangle(Shape):
    # Create a Rectangle class that inherits from Shape
    pass

def test_shapes(shape_type, **kwargs):
    # Create a shape of the specified type and test its methods
    # Return the area of the shape
    pass""",
                "test_cases": [
                    {"input": {"shape_type": "circle", "radius": 5}, "output": lambda x: abs(x - 78.54) < 0.1},
                    {"input": {"shape_type": "rectangle", "width": 4, "height": 5}, "output": 20}
                ],
                "hint": "Define the Shape class with an abstract area method. Implement specific area calculations in each derived class."
            },
            {
                "id": "vehicle_inheritance",
                "title": "Vehicle Inheritance",
                "difficulty": "Medium",
                "description": "Create a base Vehicle class with derived Car and Motorcycle classes.",
                "examples": [
                    {
                        "input": "Car('Toyota', 'Camry', 4).info()",
                        "output": "'Toyota Camry with 4 doors'",
                        "explanation": "Creates a Car object and returns information about it."
                    }
                ],
                "template": """class Vehicle:
    # Create a base Vehicle class with make and model attributes
    pass

class Car(Vehicle):
    # Create a Car class that inherits from Vehicle, with an additional doors attribute
    pass

class Motorcycle(Vehicle):
    # Create a Motorcycle class that inherits from Vehicle, with an additional type attribute
    pass

def test_vehicles(vehicle_type, make, model, **kwargs):
    # Create a vehicle of the specified type and test its methods
    # Return the result of calling info()
    pass""",
                "test_cases": [
                    {"input": {"vehicle_type": "car", "make": "Toyota", "model": "Camry", "doors": 4},
                     "output": "Toyota Camry with 4 doors"},
                    {"input": {"vehicle_type": "motorcycle", "make": "Honda", "model": "CBR", "type": "sport"},
                     "output": "Honda CBR (sport motorcycle)"}
                ],
                "hint": "Define the Vehicle class with make and model attributes. Add specific attributes and override methods in derived classes."
            }
        ]
    },
    16: {
        "name": "Comprehensions",
        "description": "Learn about dictionary and set comprehensions in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "dict_comp",
                "title": "Dictionary Comprehension",
                "difficulty": "Easy",
                "description": "Write a function that generates a dictionary of numbers and their squares using dictionary comprehension.",
                "examples": [
                    {
                        "input": "n=5",
                        "output": "{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}",
                        "explanation": "Returns a dictionary with numbers from 1 to 5 as keys and their squares as values."
                    }
                ],
                "template": """def number_squares(n):
    # Generate a dictionary of numbers and their squares using dictionary comprehension
    pass""",
                "test_cases": [
                    {"input": {"n": 5}, "output": {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}},
                    {"input": {"n": 3}, "output": {1: 1, 2: 4, 3: 9}}
                ],
                "hint": "Use dictionary comprehension with the format {x: x**2 for x in range(1, n+1)}."
            },
            {
                "id": "set_comp",
                "title": "Set Comprehension",
                "difficulty": "Easy",
                "description": "Write a function that generates a set of even numbers up to n using set comprehension.",
                "examples": [
                    {
                        "input": "n=10",
                        "output": "{2, 4, 6, 8, 10}",
                        "explanation": "Returns a set of even numbers from 1 to 10."
                    }
                ],
                "template": """def even_numbers_set(n):
    # Generate a set of even numbers up to n using set comprehension
    pass""",
                "test_cases": [
                    {"input": {"n": 10}, "output": {2, 4, 6, 8, 10}},
                    {"input": {"n": 5}, "output": {2, 4}}
                ],
                "hint": "Use set comprehension with the format {x for x in range(2, n+1, 2)}."
            },
            {
                "id": "dict_filtering",
                "title": "Dictionary Filtering",
                "difficulty": "Medium",
                "description": "Write a function that filters a dictionary to keep only key-value pairs where the value meets a condition.",
                "examples": [
                    {
                        "input": "data={'a': 1, 'b': 2, 'c': 3, 'd': 4}, min_value=3",
                        "output": "{'c': 3, 'd': 4}",
                        "explanation": "Returns a dictionary with only key-value pairs where the value is >= 3."
                    }
                ],
                "template": """def filter_dict(data, min_value):
    # Filter the dictionary to keep only pairs where value >= min_value
    # Use dictionary comprehension
    pass""",
                "test_cases": [
                    {"input": {"data": {'a': 1, 'b': 2, 'c': 3, 'd': 4}, "min_value": 3}, "output": {'c': 3, 'd': 4}},
                    {"input": {"data": {'x': 10, 'y': 20, 'z': 30}, "min_value": 15}, "output": {'y': 20, 'z': 30}}
                ],
                "hint": "Use dictionary comprehension with a condition: {k: v for k, v in data.items() if v >= min_value}."
            }
        ]
    },
    17: {
        "name": "Lambda Functions",
        "description": "Learn about lambda functions and functional programming in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "simple_lambda",
                "title": "Simple Lambda Function",
                "difficulty": "Easy",
                "description": "Write a lambda function that squares a number, and use it in a function.",
                "examples": [
                    {
                        "input": "x=5",
                        "output": "25",
                        "explanation": "Returns the square of 5, which is 25, using a lambda function."
                    }
                ],
                "template": """def apply_square(x):
    # Create a lambda function that squares a number
    # Apply it to x and return the result
    pass""",
                "test_cases": [
                    {"input": {"x": 5}, "output": 25},
                    {"input": {"x": 3}, "output": 9}
                ],
                "hint": "Define a lambda function like lambda n: n**2, then apply it to x."
            },
            {
                "id": "sort_tuples",
                "title": "Sort Tuples",
                "difficulty": "Easy",
                "description": "Write a function that sorts a list of tuples by the second element using a lambda function.",
                "examples": [
                    {
                        "input": "tuples=[(1, 5), (3, 1), (2, 3)]",
                        "output": "[(3, 1), (2, 3), (1, 5)]",
                        "explanation": "Returns the list of tuples sorted by the second element in each tuple."
                    }
                ],
                "template": """def sort_by_second(tuples):
    # Sort the list of tuples by the second element
    # Use a lambda function with the built-in sorted function
    pass""",
                "test_cases": [
                    {"input": {"tuples": [(1, 5), (3, 1), (2, 3)]}, "output": [(3, 1), (2, 3), (1, 5)]},
                    {"input": {"tuples": [(1, 1), (2, 2), (3, 3)]}, "output": [(1, 1), (2, 2), (3, 3)]}
                ],
                "hint": "Use sorted() with a lambda function as the key parameter: sorted(tuples, key=lambda x: x[1])."
            },
            {
                "id": "lambda_in_filter",
                "title": "Lambda with Filter",
                "difficulty": "Medium",
                "description": "Write a function that filters a list to keep only positive even numbers using lambda and filter.",
                "examples": [
                    {
                        "input": "numbers=[-2, -1, 0, 1, 2, 3, 4]",
                        "output": "[2, 4]",
                        "explanation": "Returns only the positive even numbers from the list."
                    }
                ],
                "template": """def filter_positive_even(numbers):
    # Filter the list to keep only positive even numbers
    # Use lambda with the filter function
    pass""",
                "test_cases": [
                    {"input": {"numbers": [-2, -1, 0, 1, 2, 3, 4]}, "output": [2, 4]},
                    {"input": {"numbers": [5, 7, 9]}, "output": []}
                ],
                "hint": "Use filter() with a lambda function that checks if a number is positive and even: filter(lambda x: x > 0 and x % 2 == 0, numbers)."
            }
        ]
    },
    18: {
        "name": "Generators",
        "description": "Learn about generators and the yield statement in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "simple_generator",
                "title": "Simple Generator",
                "difficulty": "Easy",
                "description": "Write a generator function that yields numbers from 1 to n.",
                "examples": [
                    {
                        "input": "n=5",
                        "output": "[1, 2, 3, 4, 5]",
                        "explanation": "Returns a list of numbers from 1 to 5 generated by the generator."
                    }
                ],
                "template": """def generate_numbers(n):
    # Create a generator that yields numbers from 1 to n
    pass

def test_generator(n):
    # Test the generator and return the results as a list
    pass""",
                "test_cases": [
                    {"input": {"n": 5}, "output": [1, 2, 3, 4, 5]},
                    {"input": {"n": 3}, "output": [1, 2, 3]}
                ],
                "hint": "Use a for loop with the range function and the yield statement to generate each number."
            },
            {
                "id": "fibonacci_generator",
                "title": "Fibonacci Generator",
                "difficulty": "Medium",
                "description": "Write a generator function that yields Fibonacci numbers up to n terms.",
                "examples": [
                    {
                        "input": "n=6",
                        "output": "[0, 1, 1, 2, 3, 5]",
                        "explanation": "Returns the first 6 Fibonacci numbers generated by the generator."
                    }
                ],
                "template": """def fibonacci_generator(n):
    # Create a generator that yields the first n Fibonacci numbers
    pass

def test_fibonacci(n):
    # Test the generator and return the results as a list
    pass""",
                "test_cases": [
                    {"input": {"n": 6}, "output": [0, 1, 1, 2, 3, 5]},
                    {"input": {"n": 8}, "output": [0, 1, 1, 2, 3, 5, 8, 13]}
                ],
                "hint": "Initialize two variables for the first two Fibonacci numbers (0 and 1), then use a loop to generate and yield each subsequent number."
            },
            {
                "id": "infinite_generator",
                "title": "Infinite Generator",
                "difficulty": "Medium",
                "description": "Write an infinite generator function that yields powers of 2, and a function to get the first n values.",
                "examples": [
                    {
                        "input": "n=5",
                        "output": "[1, 2, 4, 8, 16]",
                        "explanation": "Returns the first 5 powers of 2 (2^0 to 2^4) generated by the infinite generator."
                    }
                ],
                "template": """def powers_of_two():
                        # Create an infinite generator that yields powers of 2
                        pass

                    def get_first_n_powers(n):
                        # Get the first n values from the powers_of_two generator
                        pass""",
                "test_cases": [
                    {"input": {"n": 5}, "output": [1, 2, 4, 8, 16]},
                    {"input": {"n": 3}, "output": [1, 2, 4]}
                ],
                "hint": "Use an infinite loop with a counter variable and the yield statement. In the second function, use a counter to limit how many values to take from the generator."
            }
        ]
    },
    19: {
        "name": "Regular Expressions",
        "description": "Learn to use regular expressions for pattern matching in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "validate_email",
                "title": "Email Validator",
                "difficulty": "Easy",
                "description": "Write a function that validates if a string is a valid email address using regex.",
                "examples": [
                    {
                        "input": "email='user@example.com'",
                        "output": "True",
                        "explanation": "Returns True because 'user@example.com' is a valid email format."
                    }
                ],
                "template": """def is_valid_email(email):
                        # Validate if the string is a valid email address format
                        # Use the re module
                        import re
                        pass""",
                "test_cases": [
                    {"input": {"email": "user@example.com"}, "output": True},
                    {"input": {"email": "invalid-email"}, "output": False},
                    {"input": {"email": "user@example"}, "output": False}
                ],
                "hint": "Use re.match() with a pattern that checks for a username, followed by @, followed by a domain with at least one dot."
            },
            {
                "id": "extract_numbers",
                "title": "Number Extractor",
                "difficulty": "Easy",
                "description": "Write a function that extracts all numbers from a string using regex.",
                "examples": [
                    {
                        "input": "text='The price is $25.99 for 3 items.'",
                        "output": "['25.99', '3']",
                        "explanation": "Returns all numbers found in the string."
                    }
                ],
                "template": """def extract_numbers(text):
                        # Extract all numbers from the string using regex
                        # Return a list of strings
                        import re
                        pass""",
                "test_cases": [
                    {"input": {"text": "The price is $25.99 for 3 items."}, "output": ["25.99", "3"]},
                    {"input": {"text": "No numbers here!"}, "output": []}
                ],
                "hint": "Use re.findall() with a pattern that matches numbers with optional decimal parts."
            },
            {
                "id": "replace_pattern",
                "title": "Pattern Replacer",
                "difficulty": "Medium",
                "description": "Write a function that replaces all dates in a string with a specified format.",
                "examples": [
                    {
                        "input": "text='Meeting on 2023-01-15 and 2023-02-20.', format='MM/DD/YYYY'",
                        "output": "'Meeting on 01/15/2023 and 02/20/2023.'",
                        "explanation": "Replaces YYYY-MM-DD dates with MM/DD/YYYY format."
                    }
                ],
                "template": """def replace_dates(text, format='MM/DD/YYYY'):
                        # Replace all dates in YYYY-MM-DD format with the specified format
                        # Use the re module
                        import re
                        pass""",
                "test_cases": [
                    {"input": {"text": "Meeting on 2023-01-15 and 2023-02-20.", "format": "MM/DD/YYYY"},
                     "output": "Meeting on 01/15/2023 and 02/20/2023."},
                    {"input": {"text": "Event on 2023-01-15.", "format": "DD-MM-YYYY"},
                     "output": "Event on 15-01-2023."}
                ],
                "hint": "Use re.sub() with a pattern that captures the year, month, and day parts of dates, then rearrange them in the replacement string."
            }
        ]
    },
    20: {
        "name": "Decorators",
        "description": "Learn about function decorators in Python.",
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "timer_decorator",
                "title": "Timer Decorator",
                "difficulty": "Easy",
                "description": "Write a decorator that measures and prints the execution time of a function.",
                "examples": [
                    {
                        "input": "@timer\ndef slow_function()",
                        "output": "Function executed in 2.5 seconds",
                        "explanation": "The decorator measures how long the function takes to execute."
                    }
                ],
                "template": """def timer(func):
                        # Create a decorator that measures execution time
                        pass

                    def test_timer():
                        # Test the decorator with a simple function
                        # Return a string indicating success
                        pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: isinstance(x, str) and "success" in x.lower()}
                ],
                "hint": "Define a wrapper function inside the decorator that uses time.time() to measure the execution time."
            },
            {
                "id": "debug_decorator",
                "title": "Debug Decorator",
                "difficulty": "Easy",
                "description": "Write a decorator that prints the function name and arguments before execution.",
                "examples": [
                    {
                        "input": "@debug\ndef greet(name)",
                        "output": "Calling function 'greet' with args=('John',), kwargs={}",
                        "explanation": "The decorator prints debugging information when the function is called."
                    }
                ],
                "template": """def debug(func):
                        # Create a decorator that prints function name and arguments
                        pass

                    def test_debug():
                        # Test the decorator with a simple function
                        # Return a string indicating success
                        pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: isinstance(x, str) and "success" in x.lower()}
                ],
                "hint": "Define a wrapper function that prints the function name (func.__name__) and the arguments before calling the function."
            },
            {
                "id": "retry_decorator",
                "title": "Retry Decorator",
                "difficulty": "Medium",
                "description": "Write a decorator that retries a function if it raises an exception.",
                "examples": [
                    {
                        "input": "@retry(max_attempts=3)\ndef unreliable_function()",
                        "output": "Successfully executed after 2 attempts",
                        "explanation": "The decorator retries the function up to 3 times if it raises exceptions."
                    }
                ],
                "template": """def retry(max_attempts=3):
                        # Create a decorator that retries a function if it raises an exception
                        pass

                    def test_retry():
                        # Test the decorator with a function that sometimes fails
                        # Return a string indicating success
                        pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: isinstance(x, str) and "success" in x.lower()}
                ],
                "hint": "Define a decorator factory that takes max_attempts as a parameter. Inside, define a decorator that uses a try-except block to catch exceptions and retry the function."
            }
        ]
    }
}
def run_test_cases(code, test_cases):
    """Execute test cases and return results"""
    results = []
    namespace = {}

    try:
        # Execute the code in a new namespace
        exec(code, namespace)

        # Get function name from the code
        func_name = code.split('def ')[1].split('(')[0]

        # Run each test case
        for test in test_cases:
            start_time = time.time()
            try:
                result = namespace[func_name](**test['input'])
                execution_time = (time.time() - start_time) * 1000  # Convert to ms

                passed = result == test['output']
                results.append({
                    'passed': passed,
                    'input': test['input'],
                    'expected': test['output'],
                    'result': result,
                    'execution_time': execution_time
                })
            except Exception as e:
                results.append({
                    'passed': False,
                    'input': test['input'],
                    'expected': test['output'],
                    'result': f"Error: {str(e)}",
                    'execution_time': 0
                })
    except Exception as e:
        results.append({
            'passed': False,
            'input': "Code compilation",
            'expected': "Valid Python code",
            'result': f"Error: {str(e)}",
            'execution_time': 0
        })

    return results


def display_login():
    st.title("Welcome to CodeBuddy!")
    st.markdown("### Login to start coding!")

    # Create tabs for login and register
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_button"):
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                success, result = login_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_id = result
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error(result)

    with tab2:
        new_username = st.text_input("Choose Username", key="register_username")
        new_password = st.text_input("Choose Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Register", key="register_button"):
            if not new_username or not new_password:
                st.error("Please enter both username and password")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                success, result = register_user(new_username, new_password)
                if success:
                    st.success("Registration successful! You can now log in")
                    st.session_state.logged_in = True
                    st.session_state.user_id = result
                    st.session_state.username = new_username
                    st.rerun()
                else:
                    st.error(result)


def display_sidebar():
    st.sidebar.title("Navigation")

    # Display user info
    st.sidebar.markdown(f"### **User:** {st.session_state.username}")

    # Display level selector
    current_level, level_status = get_user_level(st.session_state.user_id)
    st.sidebar.markdown(f"**Current Level:** {current_level}")

    # Level navigation
    st.sidebar.markdown("### Levels")
    for level_num, level_data in LEVELS.items():
        level_name = level_data["name"]

        # Determine level status
        if level_num < current_level:
            status = "✅" if level_status.get(level_num, False) else "⚠️"
            if st.sidebar.button(f"{status} Level {level_num}: {level_name}", key=f"level_{level_num}"):
                st.session_state.current_level = level_num
                st.session_state.current_view = "level_overview"
                st.rerun()
        elif level_num == current_level:
            if st.sidebar.button(f"▶️ Level {level_num}: {level_name}", key=f"level_{level_num}"):
                st.session_state.current_level = level_num
                st.session_state.current_view = "level_overview"
                st.rerun()
        else:
            st.sidebar.button(f"🔒 Level {level_num}: {level_name}", key=f"level_{level_num}", disabled=True)

    # Logout button
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


def display_level_overview(level_num):
    level = LEVELS[level_num]
    # Calculate progress
    solved_problems = 0
    total_problems = len(level["problems"])

    conn = sqlite3.connect('python_practice.db')
    c = conn.cursor()

    problem_ids = [problem['id'] for problem in level["problems"]]
    placeholders = ", ".join(["?"] * len(problem_ids))

    c.execute(f"""
        SELECT COUNT(DISTINCT problem_id) 
        FROM submissions 
        WHERE user_id = ? AND problem_id IN ({placeholders}) AND passed = 1
        """, [st.session_state.user_id] + problem_ids)

    solved_problems = c.fetchone()[0]
    conn.close()

    progress_percentage = (solved_problems / total_problems) * 100

    # Display progress bar
    st.markdown(f"### Your Progress tracker")
    st.progress(solved_problems / total_problems)
    st.markdown(f"**Progress:** {solved_problems}/{total_problems} problems solved ({progress_percentage:.1f}%)")
    st.markdown(f"**Complete at least {level['min_problems_to_complete']} problems to unlock the next level**")
    st.title(f"Level {level_num}: {level['name']}")
    st.markdown(level["description"])

    # Show progress
    st.markdown(f"**Complete at least {level['min_problems_to_complete']} problems to unlock the next level**")

    # Display problems
    st.markdown("### Problems")
    # After calculating solved_problems
    for i, problem in enumerate(level["problems"]):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
            with col1:
                st.markdown(f"**{problem['title']}**")
            with col2:
                difficulty_class = f"difficulty-{problem['difficulty'].lower()}"
                st.markdown(f"<span class='{difficulty_class}'>{problem['difficulty']}</span>", unsafe_allow_html=True)
            with col3:
                if st.button("Solve", key=f"solve_{problem['id']}"):
                    st.session_state.current_problem = problem
                    st.session_state.current_view = "problem_detail"
                    st.rerun()
            with col4:
                # Check if this problem has been solved
                conn = sqlite3.connect('python_practice.db')
                c = conn.cursor()
                c.execute("""
                    SELECT COUNT(*) 
                    FROM submissions 
                    WHERE user_id = ? AND problem_id = ? AND passed = 1
                """, (st.session_state.user_id, problem['id']))

                is_solved = c.fetchone()[0] > 0
                conn.close()

                if is_solved:
                    st.markdown("✅")  # Green checkmark for solved problems


def display_problem_detail(problem, level_num):
    st.markdown(f"<h1 class='problem-title'>{problem['title']}</h1>", unsafe_allow_html=True)
    difficulty_class = f"difficulty-{problem['difficulty'].lower()}"
    st.markdown(f"<span class='{difficulty_class}'>{problem['difficulty']}</span> · Level {level_num}",
                unsafe_allow_html=True)

    # Problem description
    st.markdown("### Description")
    st.markdown(f"<div class='markdown-text'>{problem['description']}</div>", unsafe_allow_html=True)

    # Example cases
    st.markdown("### Examples")
    for i, example in enumerate(problem['examples'], 1):
        st.markdown(f"""<div class='example-box'>
        <strong>Example {i}:</strong><br>
        <strong>Input:</strong> {example['input']}<br>
        <strong>Output:</strong> {example['output']}<br>
        <strong>Explanation:</strong> {example['explanation']}
        </div>""", unsafe_allow_html=True)

    # Code editor
    st.markdown("### Solution")

    # Initialize code if not in session state or switched to a new problem
    if "current_code" not in st.session_state or st.session_state.get("last_problem_id") != problem["id"]:
        st.session_state.current_code = problem['template']
        st.session_state.last_problem_id = problem["id"]

    code = st_ace(value=st.session_state.current_code, language="python", theme="monokai", height=300, font_size=14,
                  key="solution_editor")
    st.session_state.current_code = code

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Submit button to test code
        if st.button("Submit", key="submit_solution"):
            with st.spinner("Running tests..."):
                results = run_test_cases(code, problem['test_cases'])

                # Display results
                all_passed = all(r['passed'] for r in results)
                total_time = sum(r['execution_time'] for r in results)

                if all_passed:
                    st.success(f"✅ All test cases passed! ({total_time:.1f}ms)")

                    # Save submission
                    save_submission(
                        st.session_state.user_id,
                        problem["id"],
                        code,
                        True,
                        total_time / 1000  # Convert to seconds
                    )

                    # Check if level completion criteria met
                    current_level, level_status = get_user_level(st.session_state.user_id)
                    if level_num == current_level:
                        # Count solved problems in this level
                        conn = sqlite3.connect('python_practice.db')
                        c = conn.cursor()

                        problem_ids = [p["id"] for p in LEVELS[level_num]["problems"]]
                        placeholders = ", ".join(["?"] * len(problem_ids))

                        c.execute(f"""
                        SELECT COUNT(DISTINCT problem_id) 
                        FROM submissions 
                        WHERE user_id = ? AND problem_id IN ({placeholders}) AND passed = 1
                        """, [st.session_state.user_id] + problem_ids)

                        solved_count = c.fetchone()[0] + 1  # +1 for current problem
                        conn.close()

                        if solved_count >= LEVELS[level_num]["min_problems_to_complete"]:
                            update_user_progress(st.session_state.user_id, level_num, True)
                            st.balloons()
                            st.success(f"🎉 Level {level_num} completed! Level {level_num + 1} unlocked!")
                else:
                    st.error("❌ Some test cases failed")

                    # Save failed submission
                    save_submission(
                        st.session_state.user_id,
                        problem["id"],
                        code,
                        False,
                        total_time / 1000  # Convert to seconds
                    )

                # Display detailed results
                for i, result in enumerate(results, 1):
                    with st.expander(f"Test Case {i}", expanded=not all_passed):
                        st.markdown(f"""```python
Input: {result['input']}
Expected: {result['expected']}
Output: {result['result']}
Time: {result['execution_time']:.1f}ms
```""")

    with col2:
        # Hint for the problem
        with st.expander("Hint"):
            st.write(problem['hint'])

    with col3:
        # Back button
        if st.button("Back to Level"):
            st.session_state.current_view = "level_overview"
            st.rerun()


def main():
    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "current_view" not in st.session_state:
        st.session_state.current_view = "level_overview"

    if "current_level" not in st.session_state:
        st.session_state.current_level = 1

    # Display login screen if not logged in
    if not st.session_state.logged_in:
        display_login()
    else:
        # Display sidebar
        display_sidebar()

        # Display main content based on current view
        if st.session_state.current_view == "level_overview":
            display_level_overview(st.session_state.current_level)
        elif st.session_state.current_view == "problem_detail":
            display_problem_detail(st.session_state.current_problem, st.session_state.current_level)


if __name__ == "__main__":
    main()
