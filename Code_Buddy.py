import streamlit as st
from streamlit_ace import st_ace

# Style configurations
st.markdown("""
<style>
    .difficulty-easy { color: #00b8a3; }
    .difficulty-medium { color: #ffc01e; }
    .difficulty-hard { color: #ff375f; }
    .test-case { background-color: #f0f2f5; padding: 10px; margin: 5px 0; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Python Basic Problems (15 problems)
PYTHON_BASIC = [
    {
        "id": 1,
        "title": "Sum of Two Numbers",
        "difficulty": "Easy",
        "description": """Write a function that returns the sum of two numbers.
        
Example:
Input: a = 3, b = 5
Output: 8

Input: a = -1, b = 1
Output: 0""",
        "template": """def add_numbers(a, b):
    # Write your code here
    pass""",
        "test_cases": [
            ((3, 5), 8),
            ((-1, 1), 0),
            ((100, 200), 300)
        ]
    },
    {
        "id": 2,
        "title": "Find Maximum",
        "difficulty": "Easy",
        "description": """Write a function that finds the maximum number in a list.
        
Example:
Input: nums = [1, 3, 2, 5, 4]
Output: 5

Input: nums = [-1, -5, -2, -8]
Output: -1""",
        "template": """def find_max(nums):
    # Write your code here
    pass""",
        "test_cases": [
            (([1, 3, 2, 5, 4],), 5),
            (([1],), 1),
            (([-1, -5, -2, -8],), -1)
        ]
    },
    {
        "id": 3,
        "title": "Count Vowels",
        "difficulty": "Easy",
        "description": """Write a function that counts the number of vowels in a string.
        
Example:
Input: text = "hello"
Output: 2

Input: text = "PYTHON"
Output: 1""",
        "template": """def count_vowels(text):
    # Write your code here
    pass""",
        "test_cases": [
            (("hello",), 2),
            (("PYTHON",), 1),
            (("aeiou",), 5)
        ]
    }
]

# Python Intermediate Problems (15 problems)
PYTHON_INTERMEDIATE = [
    {
        "id": 1,
        "title": "Fibonacci Sequence",
        "difficulty": "Medium",
        "description": """Write a function that returns the nth number in the Fibonacci sequence.
        
Example:
Input: n = 4
Output: 3
Explanation: Fibonacci sequence: 0, 1, 1, 2, 3

Input: n = 7
Output: 13
Explanation: Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13""",
        "template": """def fibonacci(n):
    # Write your code here
    pass""",
        "test_cases": [
            ((4,), 3),
            ((7,), 13),
            ((1,), 1)
        ]
    },
    {
        "id": 2,
        "title": "Anagram Check",
        "difficulty": "Medium",
        "description": """Write a function that checks if two strings are anagrams.
        
Example:
Input: s1 = "listen", s2 = "silent"
Output: True

Input: s1 = "hello", s2 = "world"
Output: False""",
        "template": """def is_anagram(s1, s2):
    # Write your code here
    pass""",
        "test_cases": [
            (("listen", "silent"), True),
            (("hello", "world"), False),
            (("python", "typhon"), True)
        ]
    }
]

# Python Advanced Problems (15 problems)
PYTHON_ADVANCED = [
    {
        "id": 1,
        "title": "LRU Cache",
        "difficulty": "Hard",
        "description": """Implement a Least Recently Used (LRU) cache with get and put methods.
        
Example:
lru = LRUCache(2)  # capacity = 2
lru.put(1, 1)
lru.put(2, 2)
lru.get(1)    # returns 1
lru.put(3, 3) # evicts key 2
lru.get(2)    # returns -1 (not found)""",
        "template": """class LRUCache:
    def __init__(self, capacity):
        # Write your code here
        pass
        
    def get(self, key):
        # Write your code here
        pass
        
    def put(self, key, value):
        # Write your code here
        pass""",
        "test_cases": [
            ((2, ["put", "put", "get", "put", "get"], [(1, 1), (2, 2), (1,), (3, 3), (2,)]), [None, None, 1, None, -1]),
        ]
    }
]

def run_test(code: str, test_case) -> dict:
    """Run a single test case and return the result"""
    try:
        # Create namespace for code execution
        namespace = {}
        exec(code, namespace)
        
        # Get function name
        func_name = code.split('def ')[1].split('(')[0]
        
        # Execute test
        args, expected = test_case
        result = namespace[func_name](*args)
        passed = result == expected
        
        return {
            'passed': passed,
            'expected': expected,
            'result': result,
            'error': None
        }
    except Exception as e:
        return {
            'passed': False,
            'expected': expected,
            'result': None,
            'error': str(e)
        }

def main():
    st.title("Python Coding Practice")
    
    # Level selection
    level = st.selectbox(
        "Select difficulty level:",
        ["Basic", "Intermediate", "Advanced"]
    )
    
    # Get problems based on level
    if level == "Basic":
        problems = PYTHON_BASIC
        color_class = "difficulty-easy"
    elif level == "Intermediate":
        problems = PYTHON_INTERMEDIATE
        color_class = "difficulty-medium"
    else:
        problems = PYTHON_ADVANCED
        color_class = "difficulty-hard"
    
    # Problem selection
    problem_titles = [f"{p['id']}. {p['title']}" for p in problems]
    selected_problem = st.selectbox("Select problem:", problem_titles)
    problem = problems[problem_titles.index(selected_problem)]
    
    # Display problem details
    st.markdown(f"<h3 class='{color_class}'>{problem['title']}</h3>", unsafe_allow_html=True)
    st.markdown(f"**Difficulty:** {problem['difficulty']}")
    st.markdown("### Problem Description")
    st.markdown(problem['description'])
    
    # Code editor
    st.markdown("### Your Solution")
    code = st_ace(
        value=problem['template'],
        language="python",
        theme="monokai",
        height=300,
        font_size=14
    )
    
    # Run tests button
    if st.button("Submit Solution"):
        with st.spinner("Running tests..."):
            all_passed = True
            
            for i, test_case in enumerate(problem['test_cases'], 1):
                result = run_test(code, test_case)
                
                if result['passed']:
                    st.success(f"✅ Test Case {i} Passed")
                else:
                    all_passed = False
                    st.error(f"❌ Test Case {i} Failed")
                
                st.markdown(f"""<div class='test-case'>
                Input: {test_case[0]}<br>
                Expected: {result['expected']}<br>
                Got: {result['result']}<br>
                {f"Error: {result['error']}" if result['error'] else ''}
                </div>""", unsafe_allow_html=True)
            
            if all_passed:
                st.balloons()
                st.success("🎉 Congratulations! All test cases passed!")

if __name__ == "__main__":
    main()
