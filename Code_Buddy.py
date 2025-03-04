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
LEVELS = {
    1: {
        "name": "Introduction to Python",
        "description": "Learn the very basics of Python programming and execution.",
        st.markdown(f"## **min_problems_to_complete**": {3}),
        "problems": [
            {
                "id": "hello_world",
                "title": "Hello, World!",
                "difficulty": "Easy",
                "description": "Write a 'Hello, World!' program and explain the Python execution process.",
                "examples": [
                    {
                        "input": "",
                        "output": "'Hello, World!'",
                        "explanation": "Your function should print the string 'Hello, World!'"
                    }
                ],
                "template": """def hello_world():
    # Write your code here to print "Hello, World!"
    # Also add a comment explaining the Python execution process
    pass""",
                "test_cases": [
                    {"input": {}, "output": "Hello, World!"}
                ],
                "hint": "Use the print() function to display the text."
            },
            {
                "id": "py_versions",
                "title": "Python 2 vs Python 3",
                "difficulty": "Easy",
                "description": "Write a function that returns a string explaining the key differences between Python 2 and Python 3 with examples.",
                "examples": [
                    {
                        "input": "",
                        "output": "A string explaining differences",
                        "explanation": "Your function should return a string with key differences."
                    }
                ],
                "template": """def python_differences():
    # Return a string explaining key differences between Python 2 and 3
    # Include at least 3 examples of syntax or feature differences
    pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: len(x) > 100 and "print" in x and "division" in x.lower()},
                    {"input": {}, "output": lambda x: "Python 2" in x and "Python 3" in x}
                ],
                "hint": "Consider differences in print syntax, division behavior, and string handling."
            },
            {
                "id": "intro_profile",
                "title": "Personal Introduction",
                "difficulty": "Easy",
                "description": "Create a function that returns your name, age, and a fun fact about yourself.",
                "examples": [
                    {
                        "input": "",
                        "output": "Name: John Doe, Age: 25, Fun Fact: I love hiking!",
                        "explanation": "Returns formatted personal information."
                    }
                ],
                "template": """def personal_info():
    # Return a string with your name, age, and a fun fact
    # Format: "Name: [name], Age: [age], Fun Fact: [fact]"
    pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: "Name:" in x and "Age:" in x and "Fun Fact:" in x},
                    {"input": {}, "output": lambda x: isinstance(x, str) and len(x) > 20}
                ],
                "hint": "Use string formatting to create the output in the required format."
            },
            {
                "id": "code_comments",
                "title": "Code Comments",
                "difficulty": "Easy",
                "description": "Write a simple function that calculates the area of a rectangle and includes proper comments explaining what the code does.",
                "examples": [
                    {
                        "input": "length=5, width=3",
                        "output": "15",
                        "explanation": "Area = length × width = 5 × 3 = 15"
                    }
                ],
                "template": """def rectangle_area(length, width):
    # Write your code here with detailed comments
    # explaining what the function does and how it works
    pass""",
                "test_cases": [
                    {"input": {"length": 5, "width": 3}, "output": 15},
                    {"input": {"length": 7, "width": 2}, "output": 14}
                ],
                "hint": "Use multiplication to calculate the area and add comments explaining each step."
            },
            {
                "id": "print_function",
                "title": "Print Function",
                "difficulty": "Medium",
                "description": "Create a function that demonstrates the use of print() with different separators and end parameters.",
                "examples": [
                    {
                        "input": "",
                        "output": "Custom output with different separators and end parameters",
                        "explanation": "Should demonstrate different print() configurations"
                    }
                ],
                "template": """def print_demo():
    # Demonstrate the print() function with different 
    # separator and end parameters
    # Return a string containing the output
    pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: "sep" in x and "end" in x and len(x) > 20},
                    {"input": {}, "output": lambda x: isinstance(x, str) and "print" in x}
                ],
                "hint": "Try using print(a, b, sep='X', end='Y') to customize output format."
            }
        ]
    },
    2: {
        "name": "Variables & Data Types",
        "description": "Learn about different data types in Python and how to use variables.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "data_types",
                "title": "Data Types",
                "difficulty": "Easy",
                "description": "Create a function that demonstrates different data types (int, float, string, boolean) and returns their types.",
                "examples": [
                    {
                        "input": "",
                        "output": "Demonstrates variable types",
                        "explanation": "The function should create variables of different types and show their types."
                    }
                ],
                "template": """def data_types_demo():
    # Create variables of different types (int, float, string, boolean)
    # Return a string showing each variable and its type
    pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: "int" in x and "float" in x and "str" in x and "bool" in x},
                    {"input": {}, "output": lambda x: isinstance(x, str) and "type" in x}
                ],
                "hint": "Use the type() function to get the type of each variable."
            },
            {
                "id": "type_conversion",
                "title": "Type Conversion",
                "difficulty": "Easy",
                "description": "Convert a string '123' to an integer and float, then perform arithmetic operations.",
                "examples": [
                    {
                        "input": "",
                        "output": "Integer: 123, Float: 123.0, Sum: 246",
                        "explanation": "Converting the string to numbers and performing operations."
                    }
                ],
                "template": """def convert_and_calculate():
    # Convert string "123" to int and float
    # Perform arithmetic operations and return the results
    pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: "123" in x and "246" in x},
                    {"input": {}, "output": lambda x: isinstance(x, str) and "Integer" in x and "Float" in x}
                ],
                "hint": "Use int() and float() functions for type conversion."
            },
            {
                "id": "rectangle_calculator",
                "title": "Rectangle Calculator",
                "difficulty": "Easy",
                "description": "Calculate the area and perimeter of a rectangle using variables.",
                "examples": [
                    {
                        "input": "length=5, width=3",
                        "output": "Area: 15, Perimeter: 16",
                        "explanation": "Area = 5×3=15, Perimeter = 2×(5+3)=16"
                    }
                ],
                "template": """def rectangle_calculator(length, width):
    # Calculate and return the area and perimeter of a rectangle
    # Return as a formatted string
    pass""",
                "test_cases": [
                    {"input": {"length": 5, "width": 3}, "output": lambda x: "Area: 15" in x and "Perimeter: 16" in x},
                    {"input": {"length": 10, "width": 4}, "output": lambda x: "Area: 40" in x and "Perimeter: 28" in x}
                ],
                "hint": "Area = length × width, Perimeter = 2 × (length + width)"
            },
            {
                "id": "temperature_converter",
                "title": "Temperature Converter",
                "difficulty": "Medium",
                "description": "Create a function that converts a Fahrenheit temperature to Celsius.",
                "examples": [
                    {
                        "input": "fahrenheit=68",
                        "output": "20.0°C",
                        "explanation": "68°F = 20°C using the formula (F - 32) × 5/9"
                    }
                ],
                "template": """def fahrenheit_to_celsius(fahrenheit):
    # Convert Fahrenheit to Celsius and return the result
    # Round to 1 decimal place
    pass""",
                "test_cases": [
                    {"input": {"fahrenheit": 68}, "output": "20.0°C"},
                    {"input": {"fahrenheit": 32}, "output": "0.0°C"}
                ],
                "hint": "The formula is C = (F - 32) × 5/9. Don't forget to format the output with the degree symbol."
            },
            {
                "id": "time_calculator",
                "title": "Time Calculator",
                "difficulty": "Medium",
                "description": "Write a function that calculates days, hours, minutes, and seconds from a given number of seconds.",
                "examples": [
                    {
                        "input": "total_seconds=90061",
                        "output": "1 day, 1 hour, 1 minute, 1 second",
                        "explanation": "90061 seconds = 1 day + 1 hour + 1 minute + 1 second"
                    }
                ],
                "template": """def time_breakdown(total_seconds):
    # Calculate days, hours, minutes, and seconds
    # Return a formatted string with the breakdown
    pass""",
                "test_cases": [
                    {"input": {"total_seconds": 90061}, "output": "1 day, 1 hour, 1 minute, 1 second"},
                    {"input": {"total_seconds": 3661}, "output": "0 days, 1 hour, 1 minute, 1 second"}
                ],
                "hint": "Use floor division and modulo to break down the total seconds into days, hours, minutes, and seconds."
            }
        ]
    },
    3: {
        "name": "String Operations",
        "description": "Learn about string manipulation and operations in Python.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "greeting",
                "title": "Greeting Generator",
                "difficulty": "Easy",
                "description": "Create a function that takes a user's first and last name and returns a greeting with their full name.",
                "examples": [
                    {
                        "input": "first_name='John', last_name='Doe'",
                        "output": "Hello, John Doe! Welcome to Python programming.",
                        "explanation": "Combines first and last name in a greeting message."
                    }
                ],
                "template": """def create_greeting(first_name, last_name):
    # Create and return a greeting with the user's full name
    pass""",
                "test_cases": [
                    {"input": {"first_name": "John", "last_name": "Doe"}, "output": "Hello, John Doe! Welcome to Python programming."},
                    {"input": {"first_name": "Jane", "last_name": "Smith"}, "output": "Hello, Jane Smith! Welcome to Python programming."}
                ],
                "hint": "Concatenate the strings or use string formatting."
            },
            {
                "id": "string_concatenation",
                "title": "String Concatenation",
                "difficulty": "Easy",
                "description": "Write a function that demonstrates different methods of string concatenation in Python.",
                "examples": [
                    {
                        "input": "",
                        "output": "Combined output showing different concatenation methods",
                        "explanation": "Shows various ways to join strings in Python."
                    }
                ],
                "template": """def concatenation_methods():
    # Demonstrate at least 3 different ways to concatenate strings
    # Return a string showing each method and its result
    pass""",
                "test_cases": [
                    {"input": {}, "output": lambda x: "+" in x and "format" in x.lower() and "join" in x.lower()},
                    {"input": {}, "output": lambda x: isinstance(x, str) and len(x) > 30}
                ],
                "hint": "Try using the + operator, the format() method, f-strings, and the join() method."
            },
            {
                "id": "char_counter",
                "title": "Character Counter",
                "difficulty": "Easy",
                "description": "Create a function that counts and returns the number of characters in a string.",
                "examples": [
                    {
                        "input": "text='Python Programming'",
                        "output": "18",
                        "explanation": "The string 'Python Programming' has 18 characters (including the space)."
                    }
                ],
                "template": """def count_characters(text):
    # Count the number of characters in the given text
    # Return the count as an integer
    pass""",
                "test_cases": [
                    {"input": {"text": "Python Programming"}, "output": 18},
                    {"input": {"text": "Hello, World!"}, "output": 13}
                ],
                "hint": "Use the len() function to get the length of a string."
            },
            {
                "id": "word_replacer",
                "title": "Word Replacer",
                "difficulty": "Medium",
                "description": "Build a function that takes a sentence and replaces all occurrences of a specific word.",
                "examples": [
                    {
                        "input": "sentence='I like apples, apples are my favorite fruit', old_word='apples', new_word='oranges'",
                        "output": "'I like oranges, oranges are my favorite fruit'",
                        "explanation": "All occurrences of 'apples' are replaced with 'oranges'."
                    }
                ],
                "template": """def replace_word(sentence, old_word, new_word):
    # Replace all occurrences of old_word with new_word in the sentence
    # Return the modified sentence
    pass""",
                "test_cases": [
                    {
                        "input": {"sentence": "I like apples, apples are my favorite fruit", "old_word": "apples", "new_word": "oranges"},
                        "output": "I like oranges, oranges are my favorite fruit"
                    },
                    {
                        "input": {"sentence": "Hello world", "old_word": "world", "new_word": "Python"},
                        "output": "Hello Python"
                    }
                ],
                "hint": "Use the replace() method or split and join operations."
            },
            {
                "id": "palindrome_checker",
                "title": "Palindrome Checker",
                "difficulty": "Medium",
                "description": "Create a function that checks if a string is a palindrome (reads the same forwards and backwards).",
                "examples": [
                    {
                        "input": "text='racecar'",
                        "output": "True",
                        "explanation": "'racecar' reads the same forwards and backwards, so it's a palindrome."
                    }
                ],
                "template": """def is_palindrome(text):
    # Check if the text is a palindrome
    # Return True if it is, False otherwise
    # Ignore case and non-alphanumeric characters
    pass""",
                "test_cases": [
                    {"input": {"text": "racecar"}, "output": True},
                    {"input": {"text": "A man, a plan, a canal: Panama"}, "output": True}
                ],
                "hint": "Remove spaces and special characters, convert to lowercase, and compare the string with its reverse."
            }
        ]
    },
    4: {
        "name": "Operators",
        "description": "Learn about different operators in Python including arithmetic, assignment, comparison, and logical operators.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "arithmetic_ops",
                "title": "Arithmetic Operators",
                "difficulty": "Easy",
                "description": "Write a function that calculates and returns the result of all arithmetic operators on two numbers.",
                "examples": [
                    {
                        "input": "a=10, b=3",
                        "output": "Addition: 13, Subtraction: 7, Multiplication: 30, Division: 3.333, Integer Division: 3, Modulus: 1, Exponentiation: 1000",
                        "explanation": "Shows the result of applying all arithmetic operators to 10 and 3."
                    }
                ],
                "template": """def arithmetic_operations(a, b):
    # Calculate and return the results of all arithmetic operations
    # Format the output as shown in the example
    pass""",
                "test_cases": [
                    {"input": {"a": 10, "b": 3}, "output": lambda x: "Addition: 13" in x and "Division: 3.333" in x and "Exponentiation: 1000" in x},
                    {"input": {"a": 5, "b": 2}, "output": lambda x: "Addition: 7" in x and "Division: 2.5" in x and "Exponentiation: 25" in x}
                ],
                "hint": "The arithmetic operators are: +, -, *, /, //, %, and **."
            },
            {
                "id": "assignment_ops",
                "title": "Assignment Operators",
                "difficulty": "Easy",
                "description": "Create a function that demonstrates the use of assignment operators in Python.",
                "examples": [
                    {
                        "input": "initial_value=10",
                        "output": "=: 10, +=: 15, -=: 5, *=: 50, /=: 5.0",
                        "explanation": "Shows the result of applying different assignment operators starting with 10."
                    }
                ],
                "template": """def assignment_operations(initial_value):
    # Demonstrate the use of assignment operators
    # Return a string showing the results of each operation
    pass""",
                "test_cases": [
                    {"input": {"initial_value": 10}, "output": lambda x: "=: 10" in x and "+=: 15" in x and "*=: 50" in x},
                    {"input": {"initial_value": 5}, "output": lambda x: "=: 5" in x and "+=: 10" in x and "*=: 25" in x}
                ],
                "hint": "Assignment operators include =, +=, -=, *=, /=, etc."
            },
            {
                "id": "comparison_ops",
                "title": "Comparison Operators",
                "difficulty": "Easy",
                "description": "Write a function that compares two numbers using all comparison operators and returns the results.",
                "examples": [
                    {
                        "input": "a=5, b=3",
                        "output": "Equal: False, Not Equal: True, Greater Than: True, Less Than: False, Greater Than or Equal: True, Less Than or Equal: False",
                        "explanation": "Shows the results of comparing 5 and 3 using all comparison operators."
                    }
                ],
                "template": """def comparison_operations(a, b):
    # Compare the two numbers using all comparison operators
    # Return a string showing the results
    pass""",
                "test_cases": [
                    {"input": {"a": 5, "b": 3}, "output": lambda x: "Equal: False" in x and "Greater Than: True" in x},
                    {"input": {"a": 10, "b": 10}, "output": lambda x: "Equal: True" in x and "Greater Than: False" in x}
                ],
                "hint": "Comparison operators include ==, !=, >, <, >=, and <=."
            },
            {
                "id": "logical_ops",
                "title": "Logical Operators",
                "difficulty": "Medium",
                "description": "Create a function that demonstrates the use of logical operators (and, or, not) with various conditions.",
                "examples": [
                    {
                        "input": "a=True, b=False",
                        "output": "a and b: False, a or b: True, not a: False, not b: True",
                        "explanation": "Shows the results of logical operations on True and False values."
                    }
                ],
                "template": """def logical_operations(a, b):
    # Demonstrate the use of logical operators
    # Return a string showing the results
    pass""",
                "test_cases": [
                    {"input": {"a": True, "b": False}, "output": lambda x: "and" in x and "or" in x and "not" in x},
                    {"input": {"a": False, "b": False}, "output": lambda x: "and: False" in x and "or: False" in x}
                ],
                "hint": "Logical operators are and, or, and not. They work with boolean values."
            },
            {
                "id": "bitwise_ops",
                "title": "Bitwise Operators",
                "difficulty": "Hard",
                "description": "Write a function that performs bitwise operations on two numbers and displays the results in binary format.",
                "examples": [
                    {
                        "input": "a=10, b=3",
                        "output": "a = 1010, b = 0011, a & b = 0010, a | b = 1011, a ^ b = 1001, ~a = -1011, a << 1 = 10100, a >> 1 = 0101",
                        "explanation": "Shows the results of bitwise operations on 10 (1010) and 3 (0011)."
                    }
                ],
                "template": """def bitwise_operations(a, b):
    # Perform bitwise operations and display results in binary
    # Return a formatted string with all operations
    pass""",
                "test_cases": [
                    {"input": {"a": 10, "b": 3}, "output": lambda x: "1010" in x and "0011" in x and "&" in x and "|" in x},
                    {"input": {"a": 5, "b": 7}, "output": lambda x: "0101" in x and "0111" in x}
                ],
                "hint": "Use bin() to convert numbers to binary strings, then use bitwise operators: &, |, ^, ~, <<, >>."
            }
        ]
    },
    5: {
        "name": "Conditional Statements",
        "description": "Learn about if, elif, and else statements to control the flow of your Python programs.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "number_sign",
                "title": "Number Sign Checker",
                "difficulty": "Easy",
                "description": "Write a function that checks if a number is positive, negative, or zero.",
                "examples": [
                    {
                        "input": "num=5",
                        "output": "'Positive'",
                        "explanation": "5 is greater than 0, so it's positive."
                    }
                ],
                "template": """def check_number_sign(num):
    # Check if the number is positive, negative, or zero
    # Return "Positive", "Negative", or "Zero"
    pass""",
                "test_cases": [
                    {"input": {"num": 5}, "output": "Positive"},
                    {"input": {"num": -3}, "output": "Negative"}
                ],
                "hint": "Use if, elif, and else statements to check the value of the number."
            },
            {
                "id": "leap_year",
                "title": "Leap Year Checker",
                "difficulty": "Easy",
                "description": "Create a function that determines if a given year is a leap year.",
                "examples": [
                    {
                        "input": "year=2020",
                        "output": "True",
                        "explanation": "2020 is divisible by 4 and not by 100, or it's divisible by 400, so it's a leap year."
                    }
                ],
                "template": """def is_leap_year(year):
    # Check if the year is a leap year
    # Return True if it is, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"year": 2020}, "output": True},
                    {"input": {"year": 2100}, "output": False}
                ],
                "hint": "A leap year is divisible by 4, except for years divisible by 100 but not by 400."
            },
            {
                "id": "grade_calculator",
                "title": "Grade Calculator",
                "difficulty": "Medium",
                "description": "Build a function that calculates the grade (A, B, C, D, F) based on a score from 0-100.",
                "examples": [
                    {
                        "input": "score=85",
                        "output": "'B'",
                        "explanation": "A score of 85 falls in the B range (80-89)."
                    }
                ],
                "template": """def calculate_grade(score):
    # Calculate the grade based on the score
    # A: 90-100, B: 80-89, C: 70-79, D: 60-69, F: 0-59
    # Return the letter grade
    pass""",
                "test_cases": [
                    {"input": {"score": 95}, "output": "A"},
                    {"input": {"score": 75}, "output": "C"}
                ],
                "hint": "Use if/elif/else statements to check the score ranges."
            },
            {
                "id": "triangle_type",
                "title": "Triangle Type",
                "difficulty": "Medium",
                "description": "Create a function that determines if a triangle is equilateral, isosceles, or scalene based on sides.",
                "examples": [
                    {
                        "input": "a=5, b=5, c=5",
                        "output": "'Equilateral'",
                        "explanation": "All sides are equal, so it's an equilateral triangle."
                    }
                ],
                "template": """def triangle_type(a, b, c):
    # Determine the type of triangle
    # Return "Equilateral", "Isosceles", or "Scalene"
    # First verify it's a valid triangle
    pass""",
                "test_cases": [
                    {"input": {"a": 5, "b": 5, "c": 5}, "output": "Equilateral"},
                    {"input": {"a": 5, "b": 5, "c": 3}, "output": "Isosceles"}
                ],
                "hint": "Check if it's a valid triangle first (sum of any two sides > third side). Then compare the sides."
            },
            {
                "id": "simple_calculator",
                "title": "Simple Calculator",
                "difficulty": "Medium",
                "description": "Write a function that implements a simple calculator (add, subtract, multiply, divide) using if-elif-else.",
                "examples": [
                    {
                        "input": "a=10, b=5, operation='+'",
                        "output": "15",
                        "explanation": "10 + 5 = 15"
                    }
                ],
                "template": """def simple_calculator(a, b, operation):
    # Implement a calculator with basic operations
    # Return the result of the operation
    # Handle division by zero
    pass""",
                "test_cases": [
                    {"input": {"a": 10, "b": 5, "operation": "+"}, "output": 15},
                    {"input": {"a": 10, "b": 0, "operation": "/"}, "output": "Error: Division by zero"}
                ],
                "hint": "Use if/elif/else to handle different operations. Check for division by zero."
            }
        ]
    },
    6: {
        "name": "Loops",
        "description": "Learn about for and while loops to repeat actions in Python.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "multiplication_table",
                "title": "Multiplication Table",
                "difficulty": "Easy",
                "description": "Write a function that displays the multiplication table of a given number.",
                "examples": [
                    {
                        "input": "num=5, range=10",
                        "output": "5 x 1 = 5\n5 x 2 = 10\n...\n5 x 10 = 50",
                        "explanation": "Shows the multiplication table for 5, up to 5 x 10."
                    }
                ],
                "template": """def multiplication_table(num, range_limit=10):
    # Generate the multiplication table for the given number
    # Return the table as a string
    pass""",
                "test_cases": [
                    {"input": {"num": 5, "range_limit": 5}, "output": lambda x: "5 x 1 = 5" in x and "5 x 5 = 25" in x and x.count("\n") == 4},
                    {"input": {"num": 3, "range_limit": 3}, "output": lambda x: "3 x 1 = 3" in x and "3 x 3 = 9" in x}
                ],
                "hint": "Use a for loop with range() to iterate through the numbers 1 to range_limit."
            },
            {
                "id": "factorial",
                "title": "Factorial Calculator",
                "difficulty": "Easy",
                "description": "Create a function that calculates the factorial of a number using a loop.",
                "examples": [
                    {
                        "input": "n=5",
                        "output": "120",
                        "explanation": "5! = 5 × 4 × 3 × 2 × 1 = 120"
                    }
                ],
                "template": """def factorial(n):
    # Calculate the factorial of n
    # Return the result
    pass""",
                "test_cases": [
                    {"input": {"n": 5}, "output": 120},
                    {"input": {"n": 0}, "output": 1}
                ],
                "hint": "Initialize a result variable to 1, then multiply it by each number from 1 to n."
            },
            {
                "id": "fibonacci",
                "title": "Fibonacci Sequence",
                "difficulty": "Medium",
                "description": "Build a function that generates the Fibonacci sequence up to a specified number of terms.",
                "examples": [
                    {
                        "input": "terms=8",
                        "output": "[0, 1, 1, 2, 3, 5, 8, 13]",
                        "explanation": "The first 8 numbers in the Fibonacci sequence."
                    }
                ],
                "template": """def fibonacci_sequence(terms):
    # Generate the Fibonacci sequence up to the specified number of terms
    # Return the sequence as a list
    pass""",
                "test_cases": [
                    {"input": {"terms": 8}, "output": [0, 1, 1, 2, 3, 5, 8, 13]},
                    {"input": {"terms": 5}, "output": [0, 1, 1, 2, 3]}
                ],
                "hint": "Initialize with the first two numbers (0 and 1), then use a loop to generate subsequent numbers by adding the previous two."
            },
            {
                "id": "prime_check",
                "title": "Prime Number Checker",
                "difficulty": "Medium",
                "description": "Write a function that checks if a number is prime.",
                "examples": [
                    {
                        "input": "num=11",
                        "output": "True",
                        "explanation": "11 is a prime number as it's only divisible by 1 and itself."
                    }
                ],
                "template": """def is_prime(num):
    # Check if the number is prime
    # Return True if it is, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"num": 11}, "output": True},
                    {"input": {"num": 4}, "output": False}
                ],
                "hint": "A prime number is greater than 1 and has no divisors other than 1 and itself. Check all numbers from 2 to the square root of the number."
            },
            {
                "id": "pyramid_pattern",
                "title": "Pyramid Pattern",
                "difficulty": "Medium",
                "description": "Create a function that prints a pyramid pattern of stars (*) with a given height.",
                "examples": [
                    {
                        "input": "height=3",
                        "output": "  *  \n *** \n*****",
                        "explanation": "A pyramid with height 3, where each row has 2*height - 1 characters (spaces and stars)."
                    }
                ],
                "template": """def pyramid(height):
    # Generate a pyramid pattern of stars (*)
    # Return the pattern as a string
    pass""",
                "test_cases": [
                    {"input": {"height": 3}, "output": "  *  \n *** \n*****"},
                    {"input": {"height": 1}, "output": "*"}
                ],
                "hint": "Use nested loops to handle rows and columns. For each row, print the right number of spaces and stars."
            }
        ]
    },
    7: {
        "name": "String Manipulation",
        "description": "Learn advanced string manipulation techniques in Python.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "string_reverse",
                "title": "String Reverser",
                "difficulty": "Easy",
                "description": "Write a function that takes a string and returns it in reverse order.",
                "examples": [
                    {
                        "input": "text='Python'",
                        "output": "'nohtyP'",
                        "explanation": "The string 'Python' reversed is 'nohtyP'."
                    }
                ],
                "template": """def reverse_string(text):
    # Reverse the given string
    # Return the reversed string
    pass""",
                "test_cases": [
                    {"input": {"text": "Python"}, "output": "nohtyP"},
                    {"input": {"text": "Hello World"}, "output": "dlroW olleH"}
                ],
                "hint": "You can use string slicing with a negative step: text[::-1]."
            },
            {
                "id": "vowel_consonant_count",
                "title": "Vowel and Consonant Counter",
                "difficulty": "Easy",
                "description": "Create a function that counts the number of vowels and consonants in a string.",
                "examples": [
                    {
                        "input": "text='Python'",
                        "output": "Vowels: 1, Consonants: 5",
                        "explanation": "'Python' has 1 vowel ('o') and 5 consonants ('P', 'y', 't', 'h', 'n')."
                    }
                ],
                "template": """def count_vowels_consonants(text):
    # Count the vowels and consonants in the text
    # Return a formatted string with the counts
    pass""",
                "test_cases": [
                    {"input": {"text": "Python"}, "output": "Vowels: 1, Consonants: 5"},
                    {"input": {"text": "Hello"}, "output": "Vowels: 2, Consonants: 3"}
                ],
                "hint": "Define a set of vowels and check each character in the string against this set. Remember to handle both uppercase and lowercase letters."
            },
            {
                "id": "extract_digits",
                "title": "Digit Extractor",
                "difficulty": "Medium",
                "description": "Build a function that extracts and displays all digits from a string.",
                "examples": [
                    {
                        "input": "text='abc123xyz456'",
                        "output": "'123456'",
                        "explanation": "The function extracts only the digits (123456) from the string 'abc123xyz456'."
                    }
                ],
                "template": """def extract_digits(text):
    # Extract all digits from the given string
    # Return a string containing only the digits
    pass""",
                "test_cases": [
                    {"input": {"text": "abc123xyz456"}, "output": "123456"},
                    {"input": {"text": "Python 3.9.0"}, "output": "390"}
                ],
                "hint": "Use the isdigit() method to check if each character is a digit, or use regular expressions with re.findall(r'\\d', text)."
            },
            {
                "id": "title_case",
                "title": "Title Case Converter",
                "difficulty": "Medium",
                "description": "Write a function that capitalizes the first letter of each word in a sentence.",
                "examples": [
                    {
                        "input": "text='welcome to python programming'",
                        "output": "'Welcome To Python Programming'",
                        "explanation": "Capitalizes the first letter of each word in the sentence."
                    }
                ],
                "template": """def title_case(text):
    # Capitalize the first letter of each word in the text
    # Return the modified string
    pass""",
                "test_cases": [
                    {"input": {"text": "welcome to python programming"}, "output": "Welcome To Python Programming"},
                    {"input": {"text": "hello world"}, "output": "Hello World"}
                ],
                "hint": "Split the string into words, capitalize each word, and then join them back together. You can also use the title() method."
            },
            {
                "id": "anagram_checker",
                "title": "Anagram Checker",
                "difficulty": "Medium",
                "description": "Create a function that checks if two strings are anagrams of each other.",
                "examples": [
                    {
                        "input": "str1='listen', str2='silent'",
                        "output": "True",
                        "explanation": "'listen' and 'silent' are anagrams because they use the same characters in different orders."
                    }
                ],
                "template": """def is_anagram(str1, str2):
    # Check if str1 and str2 are anagrams
    # Return True if they are, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"str1": "listen", "str2": "silent"}, "output": True},
                    {"input": {"str1": "hello", "str2": "world"}, "output": False}
                ],
                "hint": "Sort the characters in both strings and compare them, or count the occurrences of each character in both strings and compare the counts."
            }
        ]
    },
    8: {
        "name": "Lists",
        "description": "Learn about Python lists, their operations, and manipulations.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "min_max_finder",
                "title": "Minimum and Maximum Finder",
                "difficulty": "Easy",
                "description": "Write a function that finds the smallest and largest numbers in a list.",
                "examples": [
                    {
                        "input": "numbers=[7, 2, 9, 3, 5]",
                        "output": "Min: 2, Max: 9",
                        "explanation": "The smallest number in the list is 2, and the largest is 9."
                    }
                ],
                "template": """def find_min_max(numbers):
    # Find the minimum and maximum values in the list
    # Return a formatted string with the results
    pass""",
                "test_cases": [
                    {"input": {"numbers": [7, 2, 9, 3, 5]}, "output": "Min: 2, Max: 9"},
                    {"input": {"numbers": [-5, 0, 10]}, "output": "Min: -5, Max: 10"}
                ],
                "hint": "Use the built-in min() and max() functions, or iterate through the list tracking the current minimum and maximum values."
            },
            {
                "id": "remove_duplicates",
                "title": "Remove Duplicates",
                "difficulty": "Easy",
                "description": "Create a function that removes duplicates from a list while preserving the order.",
                "examples": [
                    {
                        "input": "items=[1, 2, 3, 2, 1, 4, 5, 5]",
                        "output": "[1, 2, 3, 4, 5]",
                        "explanation": "Removes all duplicates from the list while maintaining the original order."
                    }
                ],
                "template": """def remove_duplicates(items):
    # Remove duplicates from the list while preserving order
    # Return the list with duplicates removed
    pass""",
                "test_cases": [
                    {"input": {"items": [1, 2, 3, 2, 1, 4, 5, 5]}, "output": [1, 2, 3, 4, 5]},
                    {"input": {"items": ["a", "b", "a", "c", "b"]}, "output": ["a", "b", "c"]}
                ],
                "hint": "Use a list comprehension with a seen set, or convert to a dictionary and back to a list."
            },
            {
                "id": "merge_sorted_lists",
                "title": "Merge Sorted Lists",
                "difficulty": "Medium",
                "description": "Build a function that merges two sorted lists into a single sorted list.",
                "examples": [
                    {
                        "input": "list1=[1, 3, 5], list2=[2, 4, 6]",
                        "output": "[1, 2, 3, 4, 5, 6]",
                        "explanation": "Merges the two sorted lists into a single sorted list."
                    }
                ],
                "template": """def merge_sorted_lists(list1, list2):
    # Merge the two sorted lists into a single sorted list
    # Return the merged list
    pass""",
                "test_cases": [
                    {"input": {"list1": [1, 3, 5], "list2": [2, 4, 6]}, "output": [1, 2, 3, 4, 5, 6]},
                    {"input": {"list1": [1, 2, 3], "list2": [4, 5, 6]}, "output": [1, 2, 3, 4, 5, 6]}
                ],
                "hint": "You can use the + operator to concatenate and then sort, or implement a proper merge algorithm that maintains the existing sorting."
            },
            {
                "id": "rotate_list",
                "title": "Rotate List",
                "difficulty": "Medium",
                "description": "Write a function that rotates elements of a list to the right by k steps.",
                "examples": [
                    {
                        "input": "lst=[1, 2, 3, 4, 5], k=2",
                        "output": "[4, 5, 1, 2, 3]",
                        "explanation": "Rotating the list [1, 2, 3, 4, 5] by 2 steps to the right gives [4, 5, 1, 2, 3]."
                    }
                ],
                "template": """def rotate_list(lst, k):
    # Rotate the list to the right by k steps
    # Return the rotated list
    pass""",
                "test_cases": [
                    {"input": {"lst": [1, 2, 3, 4, 5], "k": 2}, "output": [4, 5, 1, 2, 3]},
                    {"input": {"lst": [1, 2, 3, 4, 5], "k": 0}, "output": [1, 2, 3, 4, 5]}
                ],
                "hint": "Handle k > len(lst) using modulo. Use list slicing to rotate the list, or perform k individual right rotations."
            },
            {
                "id": "stack_implementation",
                "title": "Stack Implementation",
                "difficulty": "Medium",
                "description": "Create a function that implements a stack (push, pop, display) using a list.",
                "examples": [
                    {
                        "input": "operations=['push 1', 'push 2', 'pop', 'push 3', 'display']",
                        "output": "[1, 3]",
                        "explanation": "Pushes 1, pushes 2, pops (removes 2), pushes 3, and displays the stack [1, 3]."
                    }
                ],
                "template": """def stack_operations(operations):
    # Implement a stack using a list
    # Process the operations and return the final stack
    pass""",
                "test_cases": [
                    {"input": {"operations": ["push 1", "push 2", "pop", "push 3", "display"]}, "output": [1, 3]},
                    {"input": {"operations": ["push 5", "push 7", "push 9", "pop", "display"]}, "output": [5, 7]}
                ],
                "hint": "Use a list to represent the stack. For push, use append(). For pop, use pop(). Handle the case where pop is called on an empty stack."
            }
        ]
    },
    9: {
        "name": "List Comprehension",
        "description": "Learn to use list comprehensions for more concise and readable code.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "even_numbers",
                "title": "Even Numbers Generator",
                "difficulty": "Easy",
                "description": "Write a list comprehension to get all even numbers from 1 to 50.",
                "examples": [
                    {
                        "input": "",
                        "output": "[2, 4, 6, 8, ..., 48, 50]",
                        "explanation": "Returns all even numbers from 1 to 50 using a list comprehension."
                    }
                ],
                "template": """def get_even_numbers():
    # Use a list comprehension to generate all even numbers from 1 to 50
    # Return the list of even numbers
    pass""",
                "test_cases": [
                    {"input": {}, "output": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50]},
                    {"input": {}, "output": lambda x: len(x) == 25 and all(i % 2 == 0 for i in x)}
                ],
                "hint": "Use a list comprehension with a range from 1 to 51 and filter for numbers divisible by 2."
            },
            {
                "id": "square_numbers",
                "title": "Number Squares",
                "difficulty": "Easy",
                "description": "Create a list comprehension to get squares of numbers from 1 to 20.",
                "examples": [
                    {
                        "input": "",
                        "output": "[1, 4, 9, 16, ..., 361, 400]",
                        "explanation": "Returns squares of numbers from 1 to 20 using a list comprehension."
                    }
                ],
                "template": """def get_squares():
    # Use a list comprehension to generate squares of numbers from 1 to 20
    # Return the list of squares
    pass""",
                "test_cases": [
                    {"input": {}, "output": [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361, 400]},
                    {"input": {}, "output": lambda x: len(x) == 20 and x[4] == 25}
                ],
                "hint": "Use a list comprehension with a range from 1 to 21 and calculate the square of each number."
            },
            {
                "id": "long_words",
                "title": "Long Word Filter",
                "difficulty": "Medium",
                "description": "Build a list comprehension to get all words with length greater than 5 from a given list of strings.",
                "examples": [
                    {
                        "input": "words=['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape']",
                        "output": "['banana', 'elderberry']",
                        "explanation": "Returns words with more than 5 characters from the list."
                    }
                ],
                "template": """def filter_long_words(words):
    # Use a list comprehension to filter words with length > 5
    # Return the filtered list
    pass""",
                "test_cases": [
                    {"input": {"words": ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]}, "output": ["banana", "elderberry"]},
                    {"input": {"words": ["cat", "dog", "elephant", "fox", "giraffe"]}, "output": ["elephant", "giraffe"]}
                ],
                "hint": "Use a list comprehension with a condition to check if the length of each word is greater than 5."
            },
            {
                "id": "flatten_list",
                "title": "List Flattener",
                "difficulty": "Medium",
                "description": "Write a list comprehension to flatten a 2D list into a 1D list.",
                "examples": [
                    {
                        "input": "nested_list=[[1, 2], [3, 4], [5, 6]]",
                        "output": "[1, 2, 3, 4, 5, 6]",
                        "explanation": "Flattens the nested list into a single-dimensional list."
                    }
                ],
                "template": """def flatten_2d_list(nested_list):
    # Use a list comprehension to flatten the 2D list
    # Return the flattened list
    pass""",
                "test_cases": [
                    {"input": {"nested_list": [[1, 2], [3, 4], [5, 6]]}, "output": [1, 2, 3, 4, 5, 6]},
                    {"input": {"nested_list": [[1], [2, 3], [4, 5, 6]]}, "output": [1, 2, 3, 4, 5, 6]}
                ],
                "hint": "Use a nested list comprehension with two for loops - one for the outer list and one for the inner lists."
            },
            {
                "id": "palindrome_filter",
                "title": "Palindrome Filter",
                "difficulty": "Medium",
                "description": "Create a list comprehension to filter out non-palindrome strings from a list.",
                "examples": [
                    {
                        "input": "strings=['radar', 'python', 'level', 'algorithm', 'civic']",
                        "output": "['radar', 'level', 'civic']",
                        "explanation": "Returns only the palindrome strings from the list."
                    }
                ],
                "template": """def filter_palindromes(strings):
    # Use a list comprehension to filter palindromes
    # Return the filtered list
    pass""",
                "test_cases": [
                    {"input": {"strings": ["radar", "python", "level", "algorithm", "civic"]}, "output": ["radar", "level", "civic"]},
                    {"input": {"strings": ["hello", "world", "madam", "racecar"]}, "output": ["madam", "racecar"]}
                ],
                "hint": "Use a list comprehension with a condition to check if each string equals its reverse (s == s[::-1])."
            }
        ]
    },
    10: {
        "name": "Dictionaries",
        "description": "Learn about Python dictionaries and their various operations.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "word_frequency",
                "title": "Word Frequency Counter",
                "difficulty": "Easy",
                "description": "Create a function that counts the frequency of each word in a sentence using a dictionary.",
                "examples": [
                    {
                        "input": "sentence='the quick brown fox jumps over the lazy dog'",
                        "output": "{'the': 2, 'quick': 1, 'brown': 1, 'fox': 1, 'jumps': 1, 'over': 1, 'lazy': 1, 'dog': 1}",
                        "explanation": "Returns a dictionary with the count of each word in the sentence."
                    }
                ],
                "template": """def word_frequency(sentence):
    # Count the frequency of each word in the sentence
    # Return a dictionary with words as keys and counts as values
    pass""",
                "test_cases": [
                    {"input": {"sentence": "the quick brown fox jumps over the lazy dog"}, "output": {"the": 2, "quick": 1, "brown": 1, "fox": 1, "jumps": 1, "over": 1, "lazy": 1, "dog": 1}},
                    {"input": {"sentence": "hello world hello"}, "output": {"hello": 2, "world": 1}}
                ],
                "hint": "Split the sentence into words, then use a dictionary to count occurrences. You could also use collections.Counter."
            },
            {
                "id": "phonebook",
                "title": "Phone Book Application",
                "difficulty": "Easy",
                "description": "Build a simple phone book application using dictionaries.",
                "examples": [
                    {
                        "input": "operations=['add John 1234567890', 'add Jane 9876543210', 'get John', 'remove Jane', 'get Jane']",
                        "output": "['Added John', 'Added Jane', '1234567890', 'Removed Jane', 'Not found']",
                        "explanation": "Adds John and Jane to the phone book, gets John's number, removes Jane, then tries to get Jane's number again."
                    }
                ],
                "template": """def phone_book(operations):
    # Implement a phone book with add, get, and remove operations
    # Return a list of results for each operation
    pass""",
                "test_cases": [
                    {"input": {"operations": ["add John 1234567890", "add Jane 9876543210", "get John", "remove Jane", "get Jane"]},
                     "output": ["Added John", "Added Jane", "1234567890", "Removed Jane", "Not found"]},
                    {"input": {"operations": ["add Alice 5551234", "add Bob 5555678", "remove Charlie", "add Alice 5559876", "get Alice"]},
                     "output": ["Added Alice", "Added Bob", "Not found", "Updated Alice", "5559876"]}
                ],
                "hint": "Use a dictionary to store names and phone numbers. Parse each operation string to determine the action (add, get, remove) and the parameters."
            },
            {
                "id": "merge_dicts",
                "title": "Dictionary Merger",
                "difficulty": "Medium",
                "description": "Write a function that merges two dictionaries.",
                "examples": [
                    {
                        "input": "dict1={'a': 1, 'b': 2}, dict2={'b': 3, 'c': 4}",
                        "output": "{'a': 1, 'b': 3, 'c': 4}",
                        "explanation": "Merges dict1 and dict2. When keys overlap, values from dict2 are used."
                    }
                ],
                "template": """def merge_dictionaries(dict1, dict2):
    # Merge the two dictionaries
    # When keys overlap, use the values from dict2
    # Return the merged dictionary
    pass""",
                "test_cases": [
                    {"input": {"dict1": {"a": 1, "b": 2}, "dict2": {"b": 3, "c": 4}}, "output": {"a": 1, "b": 3, "c": 4}},
                    {"input": {"dict1": {"x": 10, "y": 20}, "dict2": {"z": 30}}, "output": {"x": 10, "y": 20, "z": 30}}
                ],
                "hint": "Create a copy of dict1, then update it with dict2. Alternatively, use the ** operator to merge dictionaries in Python 3.5+."
            },
            {
                "id": "group_by_key",
                "title": "Dictionary Grouper",
                "difficulty": "Medium",
                "description": "Create a function that groups a list of dictionaries based on a specific key.",
                "examples": [
                    {
                        "input": "items=[{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}, {'name': 'Charlie', 'age': 25}], key='age'",
                        "output": "{25: [{'name': 'Alice', 'age': 25}, {'name': 'Charlie', 'age': 25}], 30: [{'name': 'Bob', 'age': 30}]}",
                        "explanation": "Groups the dictionaries by the 'age' key."
                    }
                ],
                "template": """def group_by_key(items, key):
    # Group the list of dictionaries by the specified key
    # Return a dictionary with key values as keys and lists of matching dictionaries as values
    pass""",
                "test_cases": [
                    {"input": {"items": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 25}], "key": "age"},
                     "output": {25: [{"name": "Alice", "age": 25}, {"name": "Charlie", "age": 25}], 30: [{"name": "Bob", "age": 30}]}},
                    {"input": {"items": [{"type": "fruit", "name": "apple"}, {"type": "vegetable", "name": "carrot"}, {"type": "fruit", "name": "banana"}], "key": "type"},
                     "output": {"fruit": [{"type": "fruit", "name": "apple"}, {"type": "fruit", "name": "banana"}], "vegetable": [{"type": "vegetable", "name": "carrot"}]}}
                ],
                "hint": "Create a dictionary where the keys are the values of the specified key in the dictionaries. Iterate through the items and append each dictionary to the appropriate list."
            },
            {
                "id": "library_catalog",
                "title": "Library Catalog",
                "difficulty": "Hard",
                "description": "Build a program that implements a nested dictionary to represent a simple library catalog.",
                "examples": [
                    {
                        "input": "operations=['add Python101 Programming John_Doe 2020', 'add DataScience DataAnalysis Jane_Smith 2021', 'get Python101', 'update Python101 year 2022', 'get Python101']",
                        "output": "['Added Python101', 'Added DataScience', {'title': 'Python101', 'category': 'Programming', 'author': 'John_Doe', 'year': 2020}, 'Updated Python101', {'title': 'Python101', 'category': 'Programming', 'author': 'John_Doe', 'year': 2022}]",
                        "explanation": "Creates and manages a library catalog using nested dictionaries."
                    }
                ],
                "template": """def library_catalog(operations):
    # Implement a library catalog with add, get, update, and remove operations
    # Return a list of results for each operation
    pass""",
                "test_cases": [
                    {"input": {"operations": ["add Python101 Programming John_Doe 2020", "add DataScience DataAnalysis Jane_Smith 2021", "get Python101", "update Python101 year 2022", "get Python101"]},
                     "output": ["Added Python101", "Added DataScience", {"title": "Python101", "category": "Programming", "author": "John_Doe", "year": 2020}, "Updated Python101", {"title": "Python101", "category": "Programming", "author": "John_Doe", "year": 2022}]},
                    {"input": {"operations": ["add Book1 Fiction Author1 2019", "remove Book1", "get Book1", "add Book2 NonFiction Author2 2021", "list"]},
                     "output": ["Added Book1", "Removed Book1", "Not found", "Added Book2", [{"title": "Book2", "category": "NonFiction", "author": "Author2", "year": 2021}]]}
                ],
                "hint": "Use a dictionary where keys are book titles and values are dictionaries with book details. Parse each operation string to handle add, get, update, remove, and list operations."
            }
        ]
    },
    11: {
        "name": "Tuples",
        "description": "Learn about Python tuples and their immutable nature.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "tuple_swap",
                "title": "Tuple Swap",
                "difficulty": "Easy",
                "description": "Write a function that swaps the values of two variables using tuples.",
                "examples": [
                    {
                        "input": "a=5, b=10",
                        "output": "a=10, b=5",
                        "explanation": "The values of a and b are swapped using tuple packing and unpacking."
                    }
                ],
                "template": """def swap_values(a, b):
    # Swap the values of a and b using tuples
    # Return the swapped values as a tuple (a, b)
    pass""",
                "test_cases": [
                    {"input": {"a": 5, "b": 10}, "output": (10, 5)},
                    {"input": {"a": "hello", "b": "world"}, "output": ("world", "hello")}
                ],
                "hint": "Use tuple packing and unpacking to swap values: a, b = b, a"
            },
            {
                "id": "return_multiple",
                "title": "Return Multiple Values",
                "difficulty": "Easy",
                "description": "Create a function that returns multiple values from a function using a tuple.",
                "examples": [
                    {
                        "input": "num=10",
                        "output": "(10, 100, 1000)",
                        "explanation": "Returns the number, its square, and its cube as a tuple."
                    }
                ],
                "template": """def get_number_info(num):
    # Return the number, its square, and its cube as a tuple
    pass""",
                "test_cases": [
                    {"input": {"num": 10}, "output": (10, 100, 1000)},
                    {"input": {"num": 5}, "output": (5, 25, 125)}
                ],
                "hint": "Calculate the values and return them as a tuple: return (num, num**2, num**3)"
            },
            {
                "id": "coordinate_calculator",
                "title": "Coordinate Calculator",
                "difficulty": "Medium",
                "description": "Build a function that performs operations on (x, y) coordinates stored as tuples.",
                "examples": [
                    {
                        "input": "coord1=(3, 4), coord2=(6, 8), operation='distance'",
                        "output": "5.0",
                        "explanation": "Calculates the Euclidean distance between the coordinates (3, 4) and (6, 8), which is 5."
                    }
                ],
                "template": """def coordinate_operation(coord1, coord2, operation):
    # Perform the specified operation on the two coordinates
    # Operations: 'distance', 'midpoint', 'vector_add'
    # Return the result
    pass""",
                "test_cases": [
                    {"input": {"coord1": (3, 4), "coord2": (6, 8), "operation": "distance"}, "output": 5.0},
                    {"input": {"coord1": (1, 1), "coord2": (5, 5), "operation": "midpoint"}, "output": (3, 3)}
                ],
                "hint": "Use distance = ((x2-x1)**2 + (y2-y1)**2)**0.5, midpoint = ((x1+x2)/2, (y1+y2)/2), and vector_add = (x1+x2, y1+y2)"
            },
            {
                "id": "tuple_comparison",
                "title": "Tuple Comparison",
                "difficulty": "Medium",
                "description": "Write a function that compares two tuples element by element.",
                "examples": [
                    {
                        "input": "tuple1=(1, 'a', True), tuple2=(1, 'b', False)",
                        "output": "[True, False, False]",
                        "explanation": "Compares each element: 1==1 (True), 'a'=='b' (False), True==False (False)"
                    }
                ],
                "template": """def compare_tuples(tuple1, tuple2):
    # Compare the two tuples element by element
    # Return a list of boolean values indicating equality
    pass""",
                "test_cases": [
                    {"input": {"tuple1": (1, 'a', True), "tuple2": (1, 'b', False)}, "output": [True, False, False]},
                    {"input": {"tuple1": (5, 7, 9), "tuple2": (5, 7, 9)}, "output": [True, True, True]}
                ],
                "hint": "Use a list comprehension to compare corresponding elements from both tuples."
            },
            {
                "id": "tuple_database",
                "title": "Tuple Database",
                "difficulty": "Medium",
                "description": "Create a function that uses a tuple of tuples to represent a simple database of students.",
                "examples": [
                    {
                        "input": "operations=['add John 25 CS', 'add Jane 22 Math', 'find name Jane', 'find age 25']",
                        "output": "[(John, 25, CS), (Jane, 22, Math), [(Jane, 22, Math)], [(John, 25, CS)]]",
                        "explanation": "Implements a simple database with add and find operations using tuples."
                    }
                ],
                "template": """def tuple_database(operations):
    # Implement a database with add and find operations
    # Return a list of results for each operation
    pass""",
                "test_cases": [
                    {"input": {"operations": ["add John 25 CS", "add Jane 22 Math", "find name Jane", "find age 25"]},
                     "output": [("John", 25, "CS"), ("Jane", 22, "Math"), [("Jane", 22, "Math")], [("John", 25, "CS")]]},
                    {"input": {"operations": ["add Alice 20 Physics", "add Bob 21 Chemistry", "find major Physics", "find age 21"]},
                     "output": [("Alice", 20, "Physics"), ("Bob", 21, "Chemistry"), [("Alice", 20, "Physics")], [("Bob", 21, "Chemistry")]]}
                ],
                "hint": "Use a tuple of tuples to store the database. Parse each operation string to handle add and find operations."
            }
        ]
    },
    12: {
        "name": "Sets",
        "description": "Learn about sets and set operations in Python.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "find_common",
                "title": "Common Elements Finder",
                "difficulty": "Easy",
                "description": "Write a function that finds common elements between two lists using sets.",
                "examples": [
                    {
                        "input": "list1=[1, 2, 3, 4, 5], list2=[4, 5, 6, 7, 8]",
                        "output": "{4, 5}",
                        "explanation": "The common elements between the two lists are 4 and 5."
                    }
                ],
                "template": """def find_common_elements(list1, list2):
    # Find common elements between the two lists using sets
    # Return the common elements as a set
    pass""",
                "test_cases": [
                    {"input": {"list1": [1, 2, 3, 4, 5], "list2": [4, 5, 6, 7, 8]}, "output": {4, 5}},
                    {"input": {"list1": [1, 2, 3], "list2": [4, 5, 6]}, "output": set()}
                ],
                "hint": "Convert both lists to sets and use the intersection operator (&) or the intersection() method."
            },
            {
                "id": "remove_dups_set",
                "title": "Remove Duplicates with Sets",
                "difficulty": "Easy",
                "description": "Create a function that removes duplicates from a list using sets.",
                "examples": [
                    {
                        "input": "items=[1, 2, 3, 2, 1, 4, 5, 5]",
                        "output": "[1, 2, 3, 4, 5]",
                        "explanation": "Removes all duplicates from the list using sets."
                    }
                ],
                "template": """def remove_duplicates_set(items):
    # Remove duplicates from the list using sets
    # Return the list with duplicates removed (order may not be preserved)
    pass""",
                "test_cases": [
                    {"input": {"items": [1, 2, 3, 2, 1, 4, 5, 5]}, "output": lambda x: set(x) == {1, 2, 3, 4, 5}},
                    {"input": {"items": ["a", "b", "a", "c", "b"]}, "output": lambda x: set(x) == {"a", "b", "c"}}
                ],
                "hint": "Convert the list to a set to remove duplicates, then convert back to a list."
            },
            {
                "id": "set_operations",
                "title": "Set Operations",
                "difficulty": "Medium",
                "description": "Build a function that performs set operations (union, intersection, difference, symmetric difference).",
                "examples": [
                    {
                        "input": "set1={1, 2, 3, 4}, set2={3, 4, 5, 6}, operation='union'",
                        "output": "{1, 2, 3, 4, 5, 6}",
                        "explanation": "Returns the union of set1 and set2."
                    }
                ],
                "template": """def set_operation(set1, set2, operation):
    # Perform the specified set operation
    # Operations: 'union', 'intersection', 'difference', 'symmetric_difference'
    # Return the resulting set
    pass""",
                "test_cases": [
                    {"input": {"set1": {1, 2, 3, 4}, "set2": {3, 4, 5, 6}, "operation": "union"}, "output": {1, 2, 3, 4, 5, 6}},
                    {"input": {"set1": {1, 2, 3, 4}, "set2": {3, 4, 5, 6}, "operation": "intersection"}, "output": {3, 4}}
                ],
                "hint": "Use set operations: | or union(), & or intersection(), - or difference(), ^ or symmetric_difference()."
            },
            {
                "id": "subset_superset",
                "title": "Subset and Superset Checker",
                "difficulty": "Medium",
                "description": "Write a program to check if a set is a subset or superset of another set.",
                "examples": [
                    {
                        "input": "set1={1, 2}, set2={1, 2, 3, 4}, check_type='subset'",
                        "output": "True",
                        "explanation": "set1 is a subset of set2 because all elements in set1 are also in set2."
                    }
                ],
                "template": """def check_set_relation(set1, set2, check_type):
    # Check if set1 is a subset or superset of set2
    # Return True or False
    pass""",
                "test_cases": [
                    {"input": {"set1": {1, 2}, "set2": {1, 2, 3, 4}, "check_type": "subset"}, "output": True},
                    {"input": {"set1": {1, 2, 3, 4}, "set2": {1, 2}, "check_type": "superset"}, "output": True}
                ],
                "hint": "Use subset methods: issubset() or <= for subset, issuperset() or >= for superset."
            },
            {
                "id": "unique_characters",
                "title": "Unique Characters",
                "difficulty": "Medium",
                "description": "Create a function that uses sets to find unique characters in a string.",
                "examples": [
                    {
                        "input": "text='hello world'",
                        "output": "{'h', 'e', 'l', 'o', ' ', 'w', 'r', 'd'}",
                        "explanation": "Returns a set of all unique characters in the string 'hello world'."
                    }
                ],
                "template": """def find_unique_characters(text):
    # Find all unique characters in the text using sets
    # Return the set of unique characters
    pass""",
                "test_cases": [
                    {"input": {"text": "hello world"}, "output": {"h", "e", "l", "o", " ", "w", "r", "d"}},
                    {"input": {"text": "abracadabra"}, "output": {"a", "b", "r", "c", "d"}}
                ],
                "hint": "Convert the string to a set to get all unique characters."
            }
        ]
    },
    13: {
        "name": "Functions",
        "description": "Learn advanced function techniques in Python.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "circle_calculator",
                "title": "Circle Calculator",
                "difficulty": "Easy",
                "description": "Write a function to calculate the area and perimeter of a circle.",
                "examples": [
                    {
                        "input": "radius=5",
                        "output": "(78.54, 31.42)",
                        "explanation": "Returns the area (π*r²) and perimeter (2*π*r) of a circle with radius 5."
                    }
                ],
                "template": """def circle_calculations(radius):
    # Calculate the area and perimeter of a circle
    # Return a tuple (area, perimeter) rounded to 2 decimal places
    pass""",
                "test_cases": [
                    {"input": {"radius": 5}, "output": (78.54, 31.42)},
                    {"input": {"radius": 3}, "output": (28.27, 18.85)}
                ],
                "hint": "Use the formula area = π*r² and perimeter = 2*π*r. Use 3.14159 for π or import math and use math.pi."
            },
            {
                "id": "palindrome_number",
                "title": "Palindrome Number Checker",
                "difficulty": "Easy",
                "description": "Create a function that checks if a number is a palindrome.",
                "examples": [
                    {
                        "input": "num=12321",
                        "output": "True",
                        "explanation": "12321 reads the same forwards and backwards, so it's a palindrome."
                    }
                ],
                "template": """def is_palindrome_number(num):
    # Check if the number is a palindrome
    # Return True if it is, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"num": 12321}, "output": True},
                    {"input": {"num": 12345}, "output": False}
                ],
                "hint": "Convert the number to a string and check if it equals its reverse, or compare the digits manually."
            },
            {
                "id": "simple_interest",
                "title": "Simple Interest Calculator",
                "difficulty": "Medium",
                "description": "Build a function with default parameters to calculate simple interest.",
                "examples": [
                    {
                        "input": "principal=1000, rate=5, time=2",
                        "output": "100.0",
                        "explanation": "Calculates simple interest as principal * rate * time / 100."
                    }
                ],
                "template": """def calculate_simple_interest(principal, rate=5, time=1):
    # Calculate simple interest with default parameters
    # Return the interest amount
    pass""",
                "test_cases": [
                    {"input": {"principal": 1000, "rate": 5, "time": 2}, "output": 100.0},
                    {"input": {"principal": 1000}, "output": 50.0}
                ],
                "hint": "Use the formula interest = principal * rate * time / 100, with default values for rate and time."
            },
            {
                "id": "recursive_fibonacci",
                "title": "Recursive Fibonacci",
                "difficulty": "Medium",
                "description": "Write a recursive function to calculate the nth Fibonacci number.",
                "examples": [
                    {
                        "input": "n=6",
                        "output": "8",
                        "explanation": "The 6th Fibonacci number is 8 (0, 1, 1, 2, 3, 5, 8)."
                    }
                ],
                "template": """def fibonacci_recursive(n):
    # Calculate the nth Fibonacci number recursively
    # Return the result
    pass""",
                "test_cases": [
                    {"input": {"n": 6}, "output": 8},
                    {"input": {"n": 10}, "output": 55}
                ],
                "hint": "Use the recursive definition: F(n) = F(n-1) + F(n-2), with base cases F(0) = 0 and F(1) = 1."
            },
            {
                "id": "args_kwargs",
                "title": "Args and Kwargs",
                "difficulty": "Medium",
                "description": "Create a function that uses *args and **kwargs to print formatted information.",
                "examples": [
                    {
                        "input": "args=['John', 25, 'Developer'], kwargs={'location': 'New York', 'department': 'IT'}",
                        "output": "'Name: John, Age: 25, Occupation: Developer, Extra Info: location=New York, department=IT'",
                        "explanation": "Formats the information using positional and keyword arguments."
                    }
                ],
                "template": """def format_info(*args, **kwargs):
    # Format the information using args and kwargs
    # Return the formatted string
    pass""",
                "test_cases": [
                    {"input": {"args": ["John", 25, "Developer"], "kwargs": {"location": "New York", "department": "IT"}},
                     "output": lambda x: "John" in x and "25" in x and "Developer" in x and "New York" in x},
                    {"input": {"args": ["Alice"], "kwargs": {"age": 30}},
                     "output": lambda x: "Alice" in x and "age=30" in x}
                ],
                "hint": "Process args for positional arguments and kwargs for keyword arguments, then format them in a string."
            }
        ]
    },
    14: {
        "name": "Modules",
        "description": "Learn to use Python modules to organize and reuse code.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "math_circle",
                "title": "Math Module Circle",
                "difficulty": "Easy",
                "description": "Create a program that uses the math module to calculate the area of a circle.",
                "examples": [
                    {
                        "input": "radius=5",
                        "output": "78.54",
                        "explanation": "Calculates the area of a circle using math.pi for more precision."
                    }
                ],
                "template": """def calculate_circle_area(radius):
    # Import the math module and calculate the area of a circle
    # Return the area rounded to 2 decimal places
    pass""",
                "test_cases": [
                    {"input": {"radius": 5}, "output": 78.54},
                    {"input": {"radius": 3}, "output": 28.27}
                ],
                "hint": "Import the math module and use math.pi in the formula area = π*r²."
            },
            {
                "id": "random_dice",
                "title": "Random Dice Roll",
                "difficulty": "Easy",
                "description": "Write a program that uses the random module to simulate a dice roll.",
                "examples": [
                    {
                        "input": "sides=6, rolls=3",
                        "output": "[4, 2, 6]",
                        "explanation": "Simulates rolling a 6-sided dice 3 times."
                    }
                ],
                "template": """def roll_dice(sides=6, rolls=1):
    # Import the random module and simulate dice rolls
    # Return a list of roll results
    pass""",
                "test_cases": [
                    {"input": {"sides": 6, "rolls": 3}, "output": lambda x: len(x) == 3 and all(1 <= i <= 6 for i in x)},
                    {"input": {"sides": 20, "rolls": 2}, "output": lambda x: len(x) == 2 and all(1 <= i <= 20 for i in x)}
                ],
                "hint": "Import the random module and use random.randint(1, sides) to generate random numbers between 1 and sides."
            },
            {
                "id": "datetime_age",
                "title": "Age Calculator",
                "difficulty": "Medium",
                "description": "Build a program that uses the datetime module to calculate age from birth date.",
                "examples": [
                    {
                        "input": "birth_year=1990, birth_month=5, birth_day=15",
                        "output": "A valid age calculated from the birth date to the current date.",
                        "explanation": "Calculates the age of a person born on May 15, 1990."
                    }
                ],
                "template": """def calculate_age(birth_year, birth_month, birth_day):
    # Import the datetime module and calculate age from birth date
    # Return the age in years
    pass""",
                "test_cases": [
                    {"input": {"birth_year": 1990, "birth_month": 5, "birth_day": 15}, "output": lambda x: isinstance(x, int) and x > 30},
                    {"input": {"birth_year": 2000, "birth_month": 1, "birth_day": 1}, "output": lambda x: isinstance(x, int) and 20 <= x <= 30}
                ],
                "hint": "Import the datetime module, create a date object for the birth date, and find the difference from the current date."
            },
            {
                "id": "guessing_game",
                "title": "Number Guessing Game",
                "difficulty": "Medium",
                "description": "Create a program that uses the random module to implement a simple number guessing game.",
                "examples": [
                    {
                        "input": "guesses=[25, 75, 62, 50], target=50",
                        "output": "['Higher', 'Lower', 'Lower', 'Correct!']",
                        "explanation": "Simulates a guessing game with feedback after each guess."
                    }
                ],
                "template": """def play_guessing_game(guesses, target=None):
    # Import the random module and implement a number guessing game
    # If target is None, generate a random number between 1 and 100
    # Return a list of feedback strings for each guess
    pass""",
                "test_cases": [
                    {"input": {"guesses": [25, 75, 62, 50], "target": 50}, "output": ["Higher", "Lower", "Lower", "Correct!"]},
                    {"input": {"guesses": [50, 25], "target": 30}, "output": ["Lower", "Higher"]}
                ],
                "hint": "Use random.randint(1, 100) to generate a random number. Compare each guess with the target and provide feedback."
            },
            {
                "id": "email_validator",
                "title": "Email Validator",
                "difficulty": "Medium",
                "description": "Write a program that uses the re module to validate an email address format.",
                "examples": [
                    {
                        "input": "email='user@example.com'",
                        "output": "True",
                        "explanation": "The email follows the correct format pattern."
                    }
                ],
                "template": """def validate_email(email):
    # Import the re module and validate the email format
    # Return True if valid, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"email": "user@example.com"}, "output": True},
                    {"input": {"email": "invalid.email"}, "output": False}
                ],
                "hint": "Import the re module and use a regex pattern to validate the email format. A simple pattern is '^[\\w.-]+@[\\w.-]+\\.\\w+$'."
            }
        ]
    },
    15: {
        "name": "File Handling",
        "description": "Learn to work with files in Python.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "count_lines",
                "title": "Line Counter",
                "difficulty": "Easy",
                "description": "Write a program that reads a text file and counts the number of lines.",
                "examples": [
                    {
                        "input": "file_path='sample.txt'",
                        "output": "10",
                        "explanation": "The file sample.txt contains 10 lines."
                    }
                ],
                "template": """def count_file_lines(file_path):
    # Read the file and count the number of lines
    # Return the count
    pass""",
                "test_cases": [
                    {"input": {"file_path": "sample.txt"}, "output": lambda x: isinstance(x, int) and x >= 0},
                    {"input": {"file_path": "empty.txt"}, "output": 0}
                ],
                "hint": "Open the file in read mode, use a counter or the readlines() method to count the lines."
            },
            {
                "id": "append_text",
                "title": "Text Appender",
                "difficulty": "Easy",
                "description": "Create a program that appends user input to a text file.",
                "examples": [
                    {
                        "input": "file_path='output.txt', text='Hello, World!'",
                        "output": "True",
                        "explanation": "Appends 'Hello, World!' to the file output.txt."
                    }
                ],
                "template": """def append_to_file(file_path, text):
    # Append the text to the specified file
    # Return True if successful, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"file_path": "output.txt", "text": "Hello, World!"}, "output": True},
                    {"input": {"file_path": "output.txt", "text": "Python is awesome"}, "output": True}
                ],
                "hint": "Open the file in append mode ('a') and write the text to it."
            },
            {
                "id": "csv_analyzer",
                "title": "CSV Analyzer",
                "difficulty": "Medium",
                "description": "Build a program that reads a CSV file and performs basic analysis on numerical data.",
                "examples": [
                    {
                        "input": "file_path='data.csv', column='age'",
                        "output": "{'min': 25, 'max': 45, 'avg': 35.0}",
                        "explanation": "Analyzes the 'age' column in the CSV file."
                    }
                ],
                "template": """def analyze_csv(file_path, column):
    # Read the CSV file and analyze the specified column
    # Return a dictionary with min, max, and avg values
    pass""",
                "test_cases": [
                    {"input": {"file_path": "data.csv", "column": "age"}, "output": lambda x: isinstance(x, dict) and "min" in x and "max" in x and "avg" in x},
                    {"input": {"file_path": "data.csv", "column": "salary"}, "output": lambda x: isinstance(x, dict) and "min" in x and "max" in x and "avg" in x}
                ],
                "hint": "Import the csv module to read the CSV file. Calculate min, max, and average values for the specified column."
            },
            {
                "id": "file_copy",
                "title": "File Copier",
                "difficulty": "Medium",
                "description": "Write a program that copies the contents of one file to another file.",
                "examples": [
                    {
                        "input": "source='source.txt', destination='destination.txt'",
                        "output": "True",
                        "explanation": "Copies the contents from source.txt to destination.txt."
                    }
                ],
                "template": """def copy_file(source, destination):
    # Copy the contents from the source file to the destination file
    # Return True if successful, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"source": "source.txt", "destination": "destination.txt"}, "output": True},
                    {"input": {"source": "nonexistent.txt", "destination": "destination.txt"}, "output": False}
                ],
                "hint": "Open the source file in read mode and the destination file in write mode. Read from source and write to destination."
            },
            {
                "id": "json_modifier",
                "title": "JSON Modifier",
                "difficulty": "Medium",
                "description": "Create a program that reads a JSON file, modifies it, and writes it back.",
                "examples": [
                    {
                        "input": "file_path='data.json', key='age', value=30",
                        "output": "True",
                        "explanation": "Modifies the 'age' field in the JSON file to 30."
                    }
                ],
                "template": """def modify_json(file_path, key, value):
    # Read the JSON file, modify the specified key-value pair, and write it back
    # Return True if successful, False otherwise
    pass""",
                "test_cases": [
                    {"input": {"file_path": "data.json", "key": "age", "value": 30}, "output": True},
                    {"input": {"file_path": "nonexistent.json", "key": "name", "value": "John"}, "output": False}
                ],
                "hint": "Import the json module to read and write JSON files. Load the JSON, modify the key-value pair, and dump it back."
            }
        ]
    },
    16: {
        "name": "Exception Handling",
        "description": "Learn to handle exceptions in Python.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "division_handler",
                "title": "Division By Zero Handler",
                "difficulty": "Easy",
                "description": "Write a program that handles division by zero exceptions.",
                "examples": [
                    {
                        "input": "a=5, b=0",
                        "output": "'Cannot divide by zero'",
                        "explanation": "Handles the division by zero exception and returns an error message."
                    }
                ],
                "template": """def safe_division(a, b):
    # Perform division and handle division by zero
    # Return the result or an error message
    #     pass""",
"test_cases": [
                    {"input": {"a": 5, "b": 0}, "output": "Cannot divide by zero"},
                    {"input": {"a": 10, "b": 2}, "output": 5.0}
                ],
                "hint": "Use try-except to catch ZeroDivisionError."
            },
            {
                "id": "file_handler",
                "title": "File Not Found Handler",
                "difficulty": "Easy",
                "description": "Create a program that handles file not found exceptions.",
                "examples": [
                    {
                        "input": "file_path='nonexistent.txt'",
                        "output": "'File not found: nonexistent.txt'",
                        "explanation": "Handles the file not found exception and returns an error message."
                    }
                ],
                "template": """def safe_file_read(file_path):
    # Read the file and handle file not found exception
    # Return the file contents or an error message
    pass""",
                "test_cases": [
                    {"input": {"file_path": "nonexistent.txt"}, "output": lambda x: "File not found" in x},
                    {"input": {"file_path": "sample.txt"}, "output": lambda x: isinstance(x, str) and len(x) > 0}
                ],
                "hint": "Use try-except to catch FileNotFoundError."
            },
            {
                "id": "multiple_exceptions",
                "title": "Multiple Exception Types",
                "difficulty": "Medium",
                "description": "Build a program that handles multiple exception types with different error messages.",
                "examples": [
                    {
                        "input": "operation='divide', a=5, b=0",
                        "output": "'Division error: Cannot divide by zero'",
                        "explanation": "Handles the division by zero exception with a specific error message."
                    }
                ],
                "template": """def safe_operation(operation, a, b):
    # Perform the specified operation and handle multiple exceptions
    # Operations: 'add', 'subtract', 'multiply', 'divide', 'power'
    # Return the result or an appropriate error message
    pass""",
                "test_cases": [
                    {"input": {"operation": "divide", "a": 5, "b": 0}, "output": lambda x: "divide" in x.lower() and "zero" in x.lower()},
                    {"input": {"operation": "invalid", "a": 5, "b": 2}, "output": lambda x: "operation" in x.lower() and "invalid" in x.lower()}
                ],
                "hint": "Use try-except to catch different exception types, such as ZeroDivisionError, ValueError, etc."
            },
            {
                "id": "try_except_else_finally",
                "title": "Try-Except-Else-Finally",
                "difficulty": "Medium",
                "description": "Write a program that uses try-except-else-finally blocks.",
                "examples": [
                    {
                        "input": "file_path='sample.txt'",
                        "output": "{'content': 'File content...', 'status': 'Successfully read from sample.txt'",
                        "explanation": "Reads the file and returns its content with a success message."
                    }
                ],
                "template": """def advanced_file_read(file_path):
    # Read the file using try-except-else-finally blocks
    # Return a dictionary with content and status message
    pass""",
                "test_cases": [
                    {"input": {"file_path": "sample.txt"}, "output": lambda x: isinstance(x, dict) and "content" in x and "status" in x},
                    {"input": {"file_path": "nonexistent.txt"}, "output": lambda x: isinstance(x, dict) and "error" in x and "status" in x}
                ],
                "hint": "Use try to attempt the file operation, except to catch exceptions, else for code to run if no exceptions, and finally for cleanup code."
            },
            {
                "id": "custom_exception",
                "title": "Custom Exception",
                "difficulty": "Medium",
                "description": "Create a program that implements a custom exception class.",
                "examples": [
                    {
                        "input": "age=-5",
                        "output": "'Invalid age: Age cannot be negative'",
                        "explanation": "Raises and handles a custom exception for invalid age."
                    }
                ],
                "template": """def validate_age(age):
    # Implement a custom exception class for invalid age
    # Raise the exception if age is negative
    # Return age if valid, or an error message if invalid
    pass""",
                "test_cases": [
                    {"input": {"age": -5}, "output": lambda x: "invalid" in x.lower() and "age" in x.lower() and "negative" in x.lower()},
                    {"input": {"age": 25}, "output": 25}
                ],
                "hint": "Create a custom exception class that inherits from Exception. Raise your custom exception when age is negative."
            }
        ]
    },
17: {
        "name": "OOP - Classes & Objects",
        "description": "Learn object-oriented programming concepts in Python.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "rectangle_class",
                "title": "Rectangle Class",
                "difficulty": "Easy",
                "description": "Create a simple Rectangle class with methods to calculate area and perimeter.",
                "examples": [
                    {
                        "input": "Rectangle(length=5, width=3)",
                        "output": "Area: 15, Perimeter: 16",
                        "explanation": "Creates a Rectangle object with length 5 and width 3, then calculates its area and perimeter."
                    }
                ],
                "template": """class Rectangle:
    # Implement a Rectangle class with methods to calculate area and perimeter
    pass

def test_rectangle(length, width):
    # Create a Rectangle object and test its methods
    # Return the area and perimeter as a string
    pass""",
                "test_cases": [
                    {"input": {"length": 5, "width": 3}, "output": lambda x: "Area: 15" in x and "Perimeter: 16" in x},
                    {"input": {"length": 7, "width": 2}, "output": lambda x: "Area: 14" in x and "Perimeter: 18" in x}
                ],
                "hint": "Create a class with __init__ method to initialize length and width. Implement methods to calculate area and perimeter."
            },
            {
                "id": "bank_account",
                "title": "Bank Account",
                "difficulty": "Easy",
                "description": "Build a BankAccount class with deposit, withdraw, and display balance methods.",
                "examples": [
                    {
                        "input": "BankAccount(initial_balance=100).deposit(50).withdraw(30).get_balance()",
                        "output": "120",
                        "explanation": "Creates a BankAccount with initial balance 100, deposits 50, withdraws 30, and returns the final balance of 120."
                    }
                ],
                "template": """class BankAccount:
    # Implement a BankAccount class with deposit, withdraw, and display balance methods
    pass

def test_bank_account(initial_balance, deposits, withdrawals):
    # Create a BankAccount object and test its methods
    # Return the final balance
    pass""",
                "test_cases": [
                    {"input": {"initial_balance": 100, "deposits": [50], "withdrawals": [30]}, "output": 120},
                    {"input": {"initial_balance": 200, "deposits": [100, 50], "withdrawals": [75, 25]}, "output": 250}
                ],
                "hint": "Create a class with __init__ method to initialize balance. Implement deposit, withdraw, and get_balance methods."
            },
            {
                "id": "student_class",
                "title": "Student Class",
                "difficulty": "Medium",
                "description": "Write a Student class to store and manipulate student data (name, roll number, marks).",
                "examples": [
                    {
                        "input": "Student('John', 101, [85, 90, 95]).get_average()",
                        "output": "90.0",
                        "explanation": "Creates a Student object with name 'John', roll number 101, and marks [85, 90, 95], then calculates the average marks."
                    }
                ],
                "template": """class Student:
    # Implement a Student class to store and manipulate student data
    pass

def test_student(name, roll_number, marks):
    # Create a Student object and test its methods
    # Return a dictionary with student info
    pass""",
                "test_cases": [
                    {"input": {"name": "John", "roll_number": 101, "marks": [85, 90, 95]}, "output": lambda x: isinstance(x, dict) and x.get("average") == 90.0},
                    {"input": {"name": "Alice", "roll_number": 102, "marks": [75, 80, 85]}, "output": lambda x: isinstance(x, dict) and x.get("average") == 80.0}
                ],
                "hint": "Create a class with __init__ method to initialize name, roll_number, and marks. Implement methods to calculate average, grade, etc."
            },
            {
                "id": "car_class",
                "title": "Car Class",
                "difficulty": "Medium",
                "description": "Create a Car class with attributes and methods that simulate a car's behavior.",
                "examples": [
                    {
                        "input": "Car('Toyota', 'Camry', 2020, 0).accelerate(30).accelerate(20).brake(10).get_speed()",
                        "output": "40",
                        "explanation": "Creates a Car object, accelerates twice, brakes once, and returns the final speed."
                    }
                ],
                "template": """class Car:
    # Implement a Car class with attributes and methods that simulate a car's behavior
    pass

def test_car(make, model, year, initial_speed, accelerations, brakes):
    # Create a Car object and test its methods
    # Return a dictionary with car info
    pass""",
                "test_cases": [
                    {"input": {"make": "Toyota", "model": "Camry", "year": 2020, "initial_speed": 0, "accelerations": [30, 20], "brakes": [10]}, "output": lambda x: isinstance(x, dict) and x.get("speed") == 40},
                    {"input": {"make": "Honda", "model": "Civic", "year": 2019, "initial_speed": 0, "accelerations": [40], "brakes": [15]}, "output": lambda x: isinstance(x, dict) and x.get("speed") == 25}
                ],
                "hint": "Create a class with __init__ method to initialize make, model, year, and speed. Implement methods to accelerate, brake, and get_speed."
            },
            {
                "id": "encapsulation",
                "title": "Encapsulation",
                "difficulty": "Medium",
                "description": "Build a complex class with proper encapsulation, using private attributes and getter/setter methods.",
                "examples": [
                    {
                        "input": "BankAccount('John', 1000).deposit(500).withdraw(200).get_info()",
                        "output": "{'holder': 'John', 'balance': 1300, 'transaction_count': 2}",
                        "explanation": "Creates a BankAccount object with private attributes, performs operations, and returns account info."
                    }
                ],
                "template": """class BankAccountEncapsulated:
    # Implement a BankAccount class with private attributes and getter/setter methods
    pass

def test_encapsulation(holder, initial_balance, deposits, withdrawals):
    # Create a BankAccountEncapsulated object and test its methods
    # Return the account info
    pass""",
                "test_cases": [
                    {"input": {"holder": "John", "initial_balance": 1000, "deposits": [500], "withdrawals": [200]}, "output": lambda x: isinstance(x, dict) and x.get("balance") == 1300 and x.get("transaction_count") == 2},
                    {"input": {"holder": "Alice", "initial_balance": 2000, "deposits": [300, 200], "withdrawals": [100]}, "output": lambda x: isinstance(x, dict) and x.get("balance") == 2400 and x.get("transaction_count") == 3}
                ],
                "hint": "Use the double underscore prefix (__) for private attributes. Implement getter/setter methods to access/modify these attributes."
            }
        ]
    },
    18: {
        "name": "OOP - Inheritance",
        "description": "Learn about inheritance in object-oriented programming.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "shape_hierarchy",
                "title": "Shape Hierarchy",
                "difficulty": "Easy",
                "description": "Create a base Shape class and derived Circle and Rectangle classes.",
                "examples": [
                    {
                        "input": "Circle(radius=5).area()",
                        "output": "78.54",
                        "explanation": "Creates a Circle object with radius 5, then calculates its area."
                    }
                ],
                "template": """class Shape:
    # Implement a base Shape class

class Circle(Shape):
    # Implement a Circle class inheriting from Shape

class Rectangle(Shape):
    # Implement a Rectangle class inheriting from Shape

def test_shapes(shape_type, **kwargs):
    # Create a Shape object based on shape_type and test its methods
    # Return the area and perimeter
    pass""",
                "test_cases": [
                    {"input": {"shape_type": "circle", "radius": 5}, "output": lambda x: isinstance(x, dict) and abs(x.get("area") - 78.54) < 0.01},
                    {"input": {"shape_type": "rectangle", "length": 4, "width": 3}, "output": lambda x: isinstance(x, dict) and x.get("area") == 12 and x.get("perimeter") == 14}
                ],
                "hint": "Create a base Shape class with methods that derived classes will override. Implement Circle and Rectangle classes that inherit from Shape."
            },
            {
                "id": "employee_hierarchy",
                "title": "Employee Hierarchy",
                "difficulty": "Easy",
                "description": "Build a simple Employee hierarchy with Manager and Developer subclasses.",
                "examples": [
                    {
                        "input": "Manager('John', 5000, 'IT', 3).get_salary()",
                        "output": "7000",
                        "explanation": "Creates a Manager object with base salary 5000 and 3 subordinates, then calculates the total salary."
                    }
                ],
                "template": """class Employee:
    # Implement a base Employee class

class Manager(Employee):
    # Implement a Manager class inheriting from Employee

class Developer(Employee):
    # Implement a Developer class inheriting from Employee

def test_employees(employee_type, name, base_salary, **kwargs):
    # Create an Employee object based on employee_type and test its methods
    # Return a dictionary with employee info
    pass""",
                "test_cases": [
                    {"input": {"employee_type": "manager", "name": "John", "base_salary": 5000, "department": "IT", "subordinates": 3}, "output": lambda x: isinstance(x, dict) and x.get("total_salary") == 7000},
                    {"input": {"employee_type": "developer", "name": "Alice", "base_salary": 4000, "language": "Python", "experience": 5}, "output": lambda x: isinstance(x, dict) and x.get("total_salary") == 6000}
                ],
                "hint": "Create a base Employee class with common attributes and methods. Implement Manager and Developer classes that inherit from Employee, with additional attributes and overridden methods."
            },
            {
                "id": "multilevel_inheritance",
                "title": "Multilevel Inheritance",
                "difficulty": "Medium",
                "description": "Write a program demonstrating multilevel inheritance.",
                "examples": [
                    {
                        "input": "Vehicle -> Car -> SportsCar",
                        "output": "SportsCar('Ferrari', 'F8', 2021, 340).get_info()",
                        "explanation": "Demonstrates multilevel inheritance with Vehicle as base class, Car inheriting from Vehicle, and SportsCar inheriting from Car."
                    }
                ],
                "template": """class Vehicle:
    # Implement a base Vehicle class

class Car(Vehicle):
    # Implement a Car class inheriting from Vehicle

class SportsCar(Car):
    # Implement a SportsCar class inheriting from Car

def test_multilevel_inheritance(make, model, year, top_speed):
    # Create a SportsCar object and test its methods
    # Return a dictionary with vehicle info
    pass""",
                "test_cases": [
                    {"input": {"make": "Ferrari", "model": "F8", "year": 2021, "top_speed": 340}, "output": lambda x: isinstance(x, dict) and x.get("make") == "Ferrari" and x.get("top_speed") == 340},
                    {"input": {"make": "Lamborghini", "model": "Aventador", "year": 2020, "top_speed": 350}, "output": lambda x: isinstance(x, dict) and x.get("make") == "Lamborghini" and x.get("top_speed") == 350}
                ],
                "hint": "Create a base Vehicle class, a Car class that inherits from Vehicle, and a SportsCar class that inherits from Car. Each class should have its own attributes and methods."
            },
            {
                "id": "method_override",
                "title": "Method Overriding",
                "difficulty": "Medium",
                "description": "Create a program demonstrating method overriding and super() function usage.",
                "examples": [
                    {
                        "input": "Animal -> Bird -> Penguin",
                        "output": "Penguin().move() outputs 'Waddles and swims'",
                        "explanation": "Demonstrates method overriding where Penguin overrides the move() method inherited from Bird and Animal."
                    }
                ],
                "template": """class Animal:
    # Implement a base Animal class with a move() method

class Bird(Animal):
    # Implement a Bird class inheriting from Animal with an overridden move() method
    # Use super() to call the parent class method

class Penguin(Bird):
    # Implement a Penguin class inheriting from Bird with an overridden move() method
    # Use super() to call the parent class method

def test_method_override(animal_type):
    # Create an Animal object based on animal_type and test its methods
    # Return the move behavior
    pass""",
                "test_cases": [
                    {"input": {"animal_type": "animal"}, "output": lambda x: isinstance(x, dict) and x.get("move") == "Moves"},
                    {"input": {"animal_type": "bird"}, "output": lambda x: isinstance(x, dict) and "fly" in x.get("move").lower()},
                    {"input": {"animal_type": "penguin"}, "output": lambda x: isinstance(x, dict) and "waddle" in x.get("move").lower() and "swim" in x.get("move").lower()}
                ],
                "hint": "Override the move() method in each derived class. Use super().move() to call the parent class method before adding specific behavior."
            },
            {
                "id": "university_system",
                "title": "University System",
                "difficulty": "Hard",
                "description": "Build a complex inheritance hierarchy for a university system (Person -> Student/Faculty -> Undergrad/Grad/Professor).",
                "examples": [
                    {
                        "input": "Undergrad('John', 20, '12345', 'Computer Science', 3).get_info()",
                        "output": "{'name': 'John', 'age': 20, 'id': '12345', 'major': 'Computer Science', 'year': 3, 'type': 'Undergraduate Student'}",
                        "explanation": "Creates an Undergrad object and returns its information."
                    }
                ],
                "template": """class Person:
    # Implement a base Person class

class Student(Person):
    # Implement a Student class inheriting from Person

class Faculty(Person):
    # Implement a Faculty class inheriting from Person

class Undergrad(Student):
    # Implement an Undergrad class inheriting from Student

class Grad(Student):
    # Implement a Grad class inheriting from Student

class Professor(Faculty):
    # Implement a Professor class inheriting from Faculty

def test_university_system(person_type, **kwargs):
    # Create a Person object based on person_type and test its methods
    # Return a dictionary with person info
    pass""",
                "test_cases": [
                    {"input": {"person_type": "undergrad", "name": "John", "age": 20, "id": "12345", "major": "Computer Science", "year": 3}, "output": lambda x: isinstance(x, dict) and x.get("type") == "Undergraduate Student" and x.get("major") == "Computer Science"},
                    {"input": {"person_type": "professor", "name": "Dr. Smith", "age": 45, "id": "P9876", "department": "Physics", "rank": "Associate"}, "output": lambda x: isinstance(x, dict) and x.get("type") == "Professor" and x.get("department") == "Physics"}
                ],
                "hint": "Create a hierarchy of classes starting with Person. Student and Faculty inherit from Person. Undergrad and Grad inherit from Student. Professor inherits from Faculty."
            }
        ]
    },
    19: {
        "name": "OOP - Polymorphism",
        "description": "Learn about polymorphism in object-oriented programming.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "animal_sounds",
                "title": "Animal Sounds",
                "difficulty": "Easy",
                "description": "Create a program demonstrating method overriding with different animal sound methods.",
                "examples": [
                    {
                        "input": "Dog().make_sound()",
                        "output": "'Woof!'",
                        "explanation": "Different animal classes override the make_sound() method with their specific sounds."
                    }
                ],
                "template": """class Animal:
    # Implement a base Animal class with a make_sound() method

class Dog(Animal):
    # Implement a Dog class inheriting from Animal

class Cat(Animal):
    # Implement a Cat class inheriting from Animal

class Cow(Animal):
    # Implement a Cow class inheriting from Animal

def test_animal_sounds(animal_type):
    # Create an Animal object based on animal_type and test its make_sound method
    # Return the sound
    pass""",
                "test_cases": [
                    {"input": {"animal_type": "dog"}, "output": lambda x: "woof" in x.lower()},
                    {"input": {"animal_type": "cat"}, "output": lambda x: "meow" in x.lower()},
                    {"input": {"animal_type": "cow"}, "output": lambda x: "moo" in x.lower()}
                ],
                "hint": "Create a base Animal class with a make_sound() method. Override this method in each derived class to return the specific animal sound."
            },
            {
                "id": "shape_area",
                "title": "Shape Area Methods",
                "difficulty": "Easy",
                "description": "Build a shape hierarchy with a common area() method implemented differently in each subclass.",
                "examples": [
                    {
                        "input": "Circle(radius=5).area()",
                        "output": "78.54",
                        "explanation": "Different shape classes implement the area() method according to their specific formulas."
                    }
                ],
                "template": """class Shape:
    # Implement a base Shape class with an area() method

class Circle(Shape):
    # Implement a Circle class inheriting from Shape

class Rectangle(Shape):
    # Implement a Rectangle class inheriting from Shape

class Triangle(Shape):
    # Implement a Triangle class inheriting from Shape

def test_shape_areas(shape_type, **kwargs):
    # Create a Shape object based on shape_type and test its area method
    # Return the area
    pass""",
                "test_cases": [
                    {"input": {"shape_type": "circle", "radius": 5}, "output": lambda x: abs(x - 78.54) < 0.01},
                    {"input": {"shape_type": "rectangle", "length": 4, "width": 3}, "output": 12},
                    {"input": {"shape_type": "triangle", "base": 6, "height": 4}, "output": 12}
                ],
                "hint": "Create a base Shape class with an area() method. Override this method in each derived class to calculate the area using the appropriate formula."
            },
            {
                "id": "operator_overloading",
                "title": "Operator Overloading",
                "difficulty": "Medium",
                "description": "Write a program that implements operator overloading for a custom complex number class.",
                "examples": [
                    {
                        "input": "ComplexNumber(3, 4) + ComplexNumber(2, 5)",
                        "output": "ComplexNumber(5, 9)",
                        "explanation": "Overloads the + operator to add two complex numbers."
                    }
                ],
                "template": """class ComplexNumber:
    # Implement a ComplexNumber class with operator overloading
    pass

def test_complex_numbers(a_real, a_imag, b_real, b_imag, operation):
    # Create two ComplexNumber objects and test the specified operation
    # Return the result as a dictionary
    pass""",
                "test_cases": [
                    {"input": {"a_real": 3, "a_imag": 4, "b_real": 2, "b_imag": 5, "operation": "add"}, "output": lambda x: isinstance(x, dict) and x.get("real") == 5 and x.get("imag") == 9},
                    {"input": {"a_real": 3, "a_imag": 4, "b_real": 2, "b_imag": 5, "operation": "subtract"}, "output": lambda x: isinstance(x, dict) and x.get("real") == 1 and x.get("imag") == -1}
                ],
                "hint": "Implement special methods like __add__, __sub__, __mul__, and __truediv__ to overload operators for your ComplexNumber class."
            },
            {
                "id": "duck_typing",
                "title": "Duck Typing",
                "difficulty": "Medium",
                "description": "Create a program demonstrating duck typing in Python.",
                "examples": [
                    {
                        "input": "process_speakers([Person(), Duck(), Radio()])",
                        "output": "All objects with a speak() method are processed, regardless of their type.",
                        "explanation": "Demonstrates duck typing by processing objects based on behavior rather than type."
                    }
                ],
                "template": """class Person:
    # Implement a Person class with a speak() method

class Duck:
    # Implement a Duck class with a speak() method

class Radio:
    # Implement a Radio class with a speak() method

class TV:
    # Implement a TV class without a speak() method

def process_speakers(objects):
    # Process all objects that have a speak() method
    # Return a list of outputs from each speak() method
    pass""",
                "test_cases": [
                    {"input": {"objects": ["person", "duck", "radio", "tv"]}, "output": lambda x: isinstance(x, list) and len(x) == 3},
                    {"input": {"objects": ["person", "duck"]}, "output": lambda x: isinstance(x, list) and len(x) == 2 and "person" in str(x[0]).lower() and "duck" in str(x[1]).lower()}
                ],
                "hint": "Implement classes with a speak() method. In the process_speakers function, try to call speak() on each object without checking its type, handling AttributeError for objects without the method."
            },
            {
                "id": "abstract_classes",
                "title": "Abstract Base Classes",
                "difficulty": "Hard",
                "description": "Build a program that implements abstract base classes and methods.",
                "examples": [
                    {
                        "input": "Shape is abstract -> Circle, Rectangle implement required methods",
                        "output": "Circle and Rectangle provide implementations for the abstract methods in Shape.",
                        "explanation": "Demonstrates the use of abstract base classes and methods that derived classes must implement."
                    }
                ],
                "template": """from abc import ABC, abstractmethod

class Shape(ABC):
    # Implement an abstract Shape class with abstract methods

class Circle(Shape):
    # Implement a Circle class inheriting from Shape

class Rectangle(Shape):
    # Implement a Rectangle class inheriting from Shape

def test_abstract_classes(shape_type, **kwargs):
    # Create a Shape object based on shape_type and test its methods
    # Return a dictionary with the results
    pass""",
                "test_cases": [
                    {"input": {"shape_type": "circle", "radius": 5}, "output": lambda x: isinstance(x, dict) and abs(x.get("area") - 78.54) < 0.01 and abs(x.get("perimeter") - 31.42) < 0.01},
                    {"input": {"shape_type": "rectangle", "length": 4, "width": 3}, "output": lambda x: isinstance(x, dict) and x.get("area") == 12 and x.get("perimeter") == 14}
                ],
                "hint": "Use the abc module to create an abstract base class with @abstractmethod decorators. Derived classes must implement all abstract methods."
            }
        ]
    },
20: {
        "name": "Advanced Python",
        "description": "Learn advanced Python programming concepts.",
        "min_problems_to_complete": 3,
        "problems": [
            {
                "id": "decorators",
                "title": "Decorators",
                "difficulty": "Medium",
                "description": "Write a program that implements decorators to modify function behavior.",
                "examples": [
                    {
                        "input": "@timer\ndef slow_function():",
                        "output": "The function took 2.5 seconds to execute.",
                        "explanation": "Uses a decorator to measure and display the execution time of a function."
                    }
                ],
                "template": """def timer(func):
    # Implement a timer decorator that measures function execution time
    pass

def debug(func):
    # Implement a debug decorator that prints function arguments and return value
    pass

def test_decorators(number, iterations):
    # Define a function and apply decorators to it
    # Return the results
    pass""",
                "test_cases": [
                    {"input": {"number": 10, "iterations": 1000000}, "output": lambda x: isinstance(x, dict) and "time" in x and "result" in x},
                    {"input": {"number": 5, "iterations": 500000}, "output": lambda x: isinstance(x, dict) and "time" in x and "result" in x}
                ],
                "hint": "Create a decorator function that wraps another function, adding functionality before and after the wrapped function call."
            },
            {
                "id": "generators",
                "title": "Generators",
                "difficulty": "Medium",
                "description": "Create a program that uses generators to efficiently work with large data sequences.",
                "examples": [
                    {
                        "input": "for num in fibonacci_generator(10):",
                        "output": "0, 1, 1, 2, 3, 5, 8, 13, 21, 34",
                        "explanation": "Uses a generator to produce Fibonacci numbers one at a time without storing the entire sequence in memory."
                    }
                ],
                "template": """def fibonacci_generator(n):
    # Implement a generator function that yields Fibonacci numbers
    pass

def prime_generator(max_num):
    # Implement a generator function that yields prime numbers up to max_num
    pass

def test_generators(generator_type, limit):
    # Test the specified generator function
    # Return a list of the generated values
    pass""",
                "test_cases": [
                    {"input": {"generator_type": "fibonacci", "limit": 10}, "output": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]},
                    {"input": {"generator_type": "prime", "limit": 20}, "output": [2, 3, 5, 7, 11, 13, 17, 19]}
                ],
                "hint": "Use the yield keyword to create generator functions. Generators produce values on-demand without storing the entire sequence in memory."
            },
            {
                "id": "context_managers",
                "title": "Context Managers",
                "difficulty": "Medium",
                "description": "Write a program that implements a custom context manager.",
                "examples": [
                    {
                        "input": "with Timer() as t: slow_function()",
                        "output": "The code block took 2.5 seconds to execute.",
                        "explanation": "Uses a custom context manager to measure the execution time of a code block."
                    }
                ],
                "template": """class Timer:
    # Implement a context manager that measures execution time
    pass

class TempFile:
    # Implement a context manager that creates a temporary file and cleans it up
    pass

def test_context_managers(context_manager_type, **kwargs):
    # Test the specified context manager
    # Return the results
    pass""",
                "test_cases": [
                    {"input": {"context_manager_type": "timer", "iterations": 1000000}, "output": lambda x: isinstance(x, dict) and "time" in x},
                    {"input": {"context_manager_type": "tempfile", "content": "Test content"}, "output": lambda x: isinstance(x, dict) and "content" in x and x.get("content") == "Test content"}
                ],
                "hint": "Implement __enter__ and __exit__ methods in your context manager class. The __enter__ method sets up the context and returns a value, and the __exit__ method performs cleanup."
            },
            {
                "id": "lambda_functions",
                "title": "Lambda Functions",
                "difficulty": "Medium",
                "description": "Create a program that uses lambda functions for data processing.",
                "examples": [
                    {
                        "input": "sorted(products, key=lambda x: x['price'])",
                        "output": "Products sorted by price from lowest to highest.",
                        "explanation": "Uses a lambda function as a key for sorting a list of product dictionaries by price."
                    }
                ],
                "template": """def process_data(data, operations):
    # Process the data using lambda functions
    # Operations: 'filter', 'map', 'sort', 'reduce'
    # Return the processed data
    pass

def test_lambda_functions(data, operations):
    # Test lambda functions for data processing
    # Return the processed data
    pass""",
                "test_cases": [
                    {"input": {"data": [{"name": "A", "price": 10}, {"name": "B", "price": 5}, {"name": "C", "price": 15}], "operations": ["sort_by_price"]}, "output": lambda x: isinstance(x, list) and len(x) == 3 and x[0]["price"] == 5 and x[2]["price"] == 15},
                    {"input": {"data": [1, 2, 3, 4, 5], "operations": ["filter_even", "map_square"]}, "output": [4, 16]}
                ],
                "hint": "Use lambda functions with built-in functions like filter(), map(), sorted(), and reduce() to process data concisely."
            },
            {
                "id": "threading_basics",
                "title": "Threading Basics",
                "difficulty": "Hard",
                "description": "Build a program that demonstrates basic threading concepts in Python.",
                "examples": [
                    {
                        "input": "run tasks concurrently with threads",
                        "output": "Multiple tasks executed concurrently, reducing overall execution time.",
                        "explanation": "Uses threading to run multiple tasks concurrently instead of sequentially."
                    }
                ],
                "template": """import threading
import time

def run_threads(num_threads, task_duration):
    # Implement a function that creates and runs multiple threads
    # Compare execution time with sequential execution
    # Return the results
    pass

def test_threading(num_threads, task_duration):
    # Test threading with the specified parameters
    # Return the results
    pass""",
                "test_cases": [
                    {"input": {"num_threads": 4, "task_duration": 0.1}, "output": lambda x: isinstance(x, dict) and "threaded_time" in x and "sequential_time" in x and x.get("threaded_time") < x.get("sequential_time")},
                    {"input": {"num_threads": 2, "task_duration": 0.2}, "output": lambda x: isinstance(x, dict) and "threaded_time" in x and "sequential_time" in x}
                ],
                "hint": "Use the threading module to create and start multiple threads. Each thread should execute a function that simulates work by sleeping for the specified duration."
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
