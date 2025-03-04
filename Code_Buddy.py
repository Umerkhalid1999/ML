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
        "min_problems_to_complete": 2,
        "problems": [
            {
                "id": "hello_world",
                "title": "Hello, World!",
                "difficulty": "Easy",
                "description": "Write a function that returns the string 'Hello, World!'",
                "output": "Hello, World!"
            },
            {
                "id": "name_greeting",
                "title": "Name Greeting",
                "difficulty": "Easy",
                "description": "Write a function that takes a name as input and returns a greeting.",
                "output": "Hello, {name}!"
            },
            {
                "id": "sum_two_numbers",
                "title": "Sum Two Numbers",
                "difficulty": "Easy",
                "description": "Write a function that calculates the sum of two numbers.",
                "output": "The sum of {a} and {b} is {sum}"
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
                "output": "The type of {value} is {type}"
            },
            {
                "id": "convert_to_int",
                "title": "Convert to Integer",
                "difficulty": "Easy",
                "description": "Write a function that converts a string to an integer.",
                "output": "The integer value of '{text}' is {integer_value}"
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
z
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
