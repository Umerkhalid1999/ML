import streamlit as st
import streamlit.components.v1 as components
from streamlit_ace import st_ace
import json
import time

# Configure page settings
st.set_page_config(layout="wide", page_title="Python Fundamentals Practice")

# Custom CSS for styling
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
</style>
""", unsafe_allow_html=True)

# Python Fundamentals Problems Database
PROBLEMS = {
    "basic_syntax": [
        {
            "id": 1,
            "title": "Hello World Function",
            "difficulty": "Easy",
            "category": "Basic Syntax",
            "acceptance_rate": "98%",
            "description": """Write a function that returns the string 'Hello, World!'.

This problem teaches:
1. Basic function definition
2. Return statements
3. String literals""",
            "examples": [
                {
                    "input": "hello_world()",
                    "output": '"Hello, World!"',
                    "explanation": "Function returns the greeting string"
                }
            ],
            "constraints": [
                "Return type must be string",
                "Must match exact output including punctuation"
            ],
            "template": """def hello_world():
    # Write your code here
    pass""",
            "test_cases": [
                {"input": {}, "output": "Hello, World!"}
            ],
            "hint": "Use the return statement with a string literal"
        }
    ],
    "variables_types": [
        {
            "id": 2,
            "title": "Python Data Types",
            "difficulty": "Easy",
            "category": "Variables & Types",
            "acceptance_rate": "95%",
            "description": """Create a function that demonstrates Python's basic data types.

Your function should:
1. Create variables of different types
2. Perform basic operations with them
3. Return results in a tuple""",
            "examples": [
                {
                    "input": "create_variables()",
                    "output": "(42, 3.14, 'Python', True)",
                    "explanation": "Returns different variable types in a tuple"
                }
            ],
            "constraints": [
                "Must use int, float, string, and boolean types",
                "Return must be in tuple format"
            ],
            "template": """def create_variables():
    # Create variables of different types
    # Return them in a tuple
    pass""",
            "test_cases": [
                {"input": {}, "output": (42, 3.14, "Python", True)}
            ],
            "hint": "Remember to use appropriate data types for each variable"
        }
    ],
    "strings": [
        {
            "id": 3,
            "title": "String Operations",
            "difficulty": "Easy",
            "category": "Strings",
            "acceptance_rate": "92%",
            "description": """Write a function that performs basic string operations.

The function should:
1. Convert a string to uppercase
2. Get string length
3. Slice the first 3 characters
4. Return all results in a tuple""",
            "examples": [
                {
                    "input": 'process_string("python")',
                    "output": '("PYTHON", 6, "pyt")',
                    "explanation": "Returns uppercase, length, and first 3 chars"
                }
            ],
            "constraints": [
                "Input will be a non-empty string",
                "Return tuple must contain all three operations"
            ],
            "template": """def process_string(text):
    # Write your code here
    pass""",
            "test_cases": [
                {"input": {"text": "python"}, "output": ("PYTHON", 6, "pyt")},
                {"input": {"text": "code"}, "output": ("CODE", 4, "cod")}
            ],
            "hint": "Use string methods like .upper() and string slicing"
        }
    ],
    "control_flow": [
        {
            "id": 4,
            "title": "If-Else Practice",
            "difficulty": "Easy",
            "category": "Control Flow",
            "acceptance_rate": "90%",
            "description": """Write a function that uses if-else statements to categorize numbers.

The function should:
1. Take a number as input
2. Return "Positive" if number > 0
3. Return "Negative" if number < 0
4. Return "Zero" if number = 0""",
            "examples": [
                {
                    "input": "categorize_number(5)",
                    "output": '"Positive"',
                    "explanation": "5 is greater than 0"
                }
            ],
            "constraints": [
                "Input will be an integer",
                "Return must be one of three strings"
            ],
            "template": """def categorize_number(num):
    # Write your code here
    pass""",
            "test_cases": [
                {"input": {"num": 5}, "output": "Positive"},
                {"input": {"num": -3}, "output": "Negative"},
                {"input": {"num": 0}, "output": "Zero"}
            ],
            "hint": "Use if-elif-else statements to check number properties"
        }
    ]
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

def main():
    # Sidebar navigation
    st.sidebar.title("Python Fundamentals")
    category = st.sidebar.selectbox(
        "Select Category",
        ["Basic Syntax", "Variables & Types", "Strings", "Control Flow", 
         "Functions", "Lists", "Dictionaries", "OOP Basics", 
         "File Handling", "Exception Handling"]
    )
    
    difficulty = st.sidebar.selectbox(
        "Difficulty",
        ["All", "Easy", "Medium", "Hard"]
    )
    
    # Track progress (you can expand this with session state)
    if 'problems_completed' not in st.session_state:
        st.session_state.problems_completed = set()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Map selected category to problems dictionary key
        category_key = category.lower().replace(" ", "_")
        if category_key in PROBLEMS:
            problems = PROBLEMS[category_key]
            
            # Select problem (for now using first problem in category)
            problem = problems[0]
            
            # Problem header
            st.markdown(f"<h1 class='problem-title'>{problem['id']}. {problem['title']}</h1>", unsafe_allow_html=True)
            
            difficulty_class = f"difficulty-{problem['difficulty'].lower()}"
            st.markdown(f"<span class='{difficulty_class}'>{problem['difficulty']}</span> · Acceptance Rate: {problem['acceptance_rate']}", unsafe_allow_html=True)
            
            # Problem description
            st.markdown("### Description")
            st.markdown(f"<div class='markdown-text'>{problem['description']}</div>", unsafe_allow_html=True)
            
            # Examples
            st.markdown("### Examples")
            for i, example in enumerate(problem['examples'], 1):
                st.markdown(f"""<div class='example-box'>
                <strong>Example {i}:</strong><br>
                <strong>Input:</strong> {example['input']}<br>
                <strong>Output:</strong> {example['output']}<br>
                <strong>Explanation:</strong> {example['explanation']}
                </div>""", unsafe_allow_html=True)
            
            # Constraints
            st.markdown("### Constraints")
            for constraint in problem['constraints']:
                st.markdown(f"• {constraint}")
            
            # Code editor
            st.markdown("### Solution")
            code = st_ace(
                value=problem['template'],
                language="python",
                theme="monokai",
                height=300,
                font_size=14,
                key="solution_editor"
            )
            
            # Submit button and test results
            if st.button("Submit", key="submit_solution"):
                with st.spinner("Running tests..."):
                    results = run_test_cases(code, problem['test_cases'])
                    
                    # Display results
                    all_passed = all(r['passed'] for r in results)
                    total_time = sum(r['execution_time'] for r in results)
                    
                    if all_passed:
                        st.success(f"✅ All test cases passed! ({total_time:.1f}ms)")
                        st.session_state.problems_completed.add(problem['id'])
                    else:
                        st.error("❌ Some test cases failed")
                    
                    # Detailed results
                    for i, result in enumerate(results, 1):
                        with st.expander(f"Test Case {i}", expanded=not all_passed):
                            st.markdown(f"""```python
Input: {result['input']}
Expected: {result['expected']}
Output: {result['result']}
Time: {result['execution_time']:.1f}ms
```""")
        else:
            st.info("More problems coming soon for this category!")
    
    # Right sidebar for problem stats and hints
    with col2:
        st.markdown("### Your Progress")
        st.markdown(f"Problems Completed: {len(st.session_state.problems_completed)}")
        
        st.markdown("### Problem Stats")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""<div class='stats-box'>
            Acceptance<br>
            <strong>{problem['acceptance_rate']}</strong>
            </div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""<div class='stats-box'>
            Difficulty<br>
            <strong class='{difficulty_class}'>{problem['difficulty']}</strong>
            </div>""", unsafe_allow_html=True)
        
        # Hints
        with st.expander("Hint"):
            st.write(problem['hint'])

if __name__ == "__main__":
    main()
